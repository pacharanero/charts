#!/usr/bin/env python3
"""Suggest tags for all chart files based on artist, content, and chord analysis."""
import re
from pathlib import Path
from collections import Counter

CHARTS_DIR = Path(__file__).resolve().parent.parent / "charts"

# Known artist -> genre/era mappings
ARTIST_TAGS = {
    'bill haley': ['rockabilly', '50s', 'rock-and-roll'],
    'bill haley & his comets': ['rockabilly', '50s', 'rock-and-roll'],
    'brian setzer': ['rockabilly', 'swing-revival', 'stray-cats'],
    'brian setzer orchestra': ['swing-revival', 'big-band', 'jump-blues'],
    'stray cats': ['rockabilly', '80s', 'psychobilly'],
    'imelda may': ['rockabilly', 'irish', 'modern'],
    'big bad voodoo daddy': ['swing-revival', '90s', 'neo-swing'],
    'cherry poppin daddies': ['swing-revival', 'ska', '90s'],
    'roy orbison': ['rock-and-roll', '60s', 'ballad'],
    'elvis presley': ['rock-and-roll', '50s', 'rockabilly'],
    'the beatles': ['60s', 'british-invasion', 'rock'],
    'the rolling stones': ['60s', 'blues-rock', 'rock'],
    'the who': ['60s', 'british-invasion', 'rock'],
    'green day': ['punk', '90s', 'pop-punk'],
    'oasis': ['britpop', '90s', 'rock'],
    'kaiser chiefs': ['indie', '00s', 'britpop'],
    'tenacious d': ['comedy-rock', '00s', 'hard-rock'],
    'monty python': ['comedy', 'novelty'],
    'eric idle': ['comedy', 'novelty'],
    'tim minchin': ['comedy', 'piano', 'modern'],
    'flight of the conchords': ['comedy', 'folk', 'novelty'],
    'hozier': ['indie', 'soul', 'modern'],
    'steve wonder': ['soul', 'funk', '70s'],
    'stevie wonder': ['soul', 'funk', '70s'],
    'bill withers': ['soul', '70s', 'acoustic'],
    'johnny cash': ['country', 'rockabilly', 'americana'],
    'dolly parton': ['country', '70s'],
    'bob dylan': ['folk', '60s', 'singer-songwriter'],
    'simon & garfunkel': ['folk', '60s', 'singer-songwriter'],
    'cat stevens': ['folk', '70s', 'singer-songwriter'],
    'ed sheeran': ['pop', 'modern', 'singer-songwriter'],
    'fountains of wayne': ['power-pop', '90s', '00s'],
    'the police': ['80s', 'new-wave', 'rock'],
    'the kinks': ['60s', 'british-invasion', 'rock'],
    'r.e.m.': ['80s', 'alternative', 'rock'],
    'rem': ['80s', 'alternative', 'rock'],
    'toto': ['80s', 'pop', 'rock'],
    'alestorm': ['folk-metal', 'comedy', 'metal'],
    'daft punk': ['electronic', '00s', 'funk'],
    'georgie fame': ['60s', 'r&b', 'soul'],
    'randy newman': ['singer-songwriter', 'soundtrack', '70s'],
    'traditional': ['folk', 'traditional', 'irish'],
    'soggy bottom boys': ['country', 'soundtrack', 'americana'],
    'tenpole tudor': ['punk', 'new-wave', '80s'],
    'shakin stevens': ['rockabilly', '80s', 'pop'],
    'slade': ['glam-rock', '70s', 'rock'],
    'nirvana': ['grunge', '90s', 'alternative'],
    'dire straits': ['rock', '80s', 'blues-rock'],
    'mark knopfler': ['rock', 'blues-rock', 'singer-songwriter'],
    'queen': ['70s', 'rock', 'glam-rock'],
    'freddie mercury': ['70s', 'rock', 'glam-rock'],
    'the doors': ['60s', 'psychedelic', 'rock'],
    'shocking blue': ['60s', 'psychedelic', 'rock'],
    'nina simone': ['jazz', 'soul', 'blues'],
    'ella fitzgerald': ['jazz', 'swing', 'vocal-jazz'],
    'frank sinatra': ['jazz', 'swing', 'vocal-jazz'],
    'bobby darin': ['swing', '50s', '60s', 'vocal-jazz'],
    'patti labelle': ['funk', '70s', 'soul'],
    'mary wells': ['motown', '60s', 'soul'],
    'the drifters': ['50s', '60s', 'soul', 'doo-wop'],
    'aretha franklin': ['soul', '60s', 'r&b'],
    'wilson pickett': ['soul', '60s', 'r&b'],
    'ruth brown': ['r&b', '50s', 'blues'],
    'wand jackson': ['rockabilly', 'country', '50s'],
    'janis martin': ['rockabilly', '50s', 'rock-and-roll'],
    'janis joplin': ['blues-rock', '60s', 'psychedelic'],
    'big brother & the holding company': ['blues-rock', '60s', 'psychedelic'],
    'the black crowes': ['blues-rock', '90s', 'southern-rock'],
    't-bone walker': ['blues', 'electric-blues', '40s'],
    'robbie williams': ['pop', '90s', '00s'],
    'lonnie donegan': ['skiffle', '50s', 'folk'],
    'the bobby fuller four': ['60s', 'garage-rock', 'rock'],
    'the crickets': ['50s', 'rock-and-roll', 'rockabilly'],
    'levellers': ['folk-rock', '90s', 'celtic'],
    'kylie minogue': ['pop', 'dance', '00s'],
    'maneskin': ['rock', 'modern', 'italian'],
    'fairground attraction': ['folk', '80s', 'acoustic'],
    'hillbilly moon explosion': ['rockabilly', 'modern', 'swiss'],
    'the hillbilly hellcats': ['rockabilly', 'modern', 'danish'],
    'harrison rimmer': ['instrumental', 'modern', 'guitar'],
    'joe satriani': ['instrumental', 'rock', 'guitar'],
    'nuno bettencourt': ['instrumental', 'rock', 'guitar', 'extreme'],
    'extreme': ['rock', '80s', '90s'],
    'link wray': ['instrumental', '50s', 'rock-and-roll'],
    'the super lounge orchestra': ['lounge', 'instrumental', 'modern'],
    'bebo best': ['lounge', 'instrumental', 'modern'],
}

def analyze_chords(content):
    chords = set(re.findall(r'\[([^\]]+)\]', content))
    has_jazz = any(re.search(r'(maj7|m7|dim|aug|9|11|13|sus|add)', c) for c in chords)
    has_capo = 'capo' in content.lower()
    has_tab = '```text' in content
    return {'jazz-chords': has_jazz, 'capo': has_capo, 'tab': has_tab}

def suggest_tags_for_file(filepath: Path) -> tuple[str, str, str, list[str]]:
    content = filepath.read_text(encoding='utf-8')
    
    title_m = re.search(r'^title:\s*"([^"]+)"', content, re.MULTILINE)
    artist_m = re.search(r'^## (.+)$', content, re.MULTILINE)
    
    title = title_m.group(1) if title_m else filepath.stem
    artist = artist_m.group(1).strip() if artist_m else 'unknown'
    artist_lower = artist.lower()
    
    tags = set()
    for known_artist, artist_tags in ARTIST_TAGS.items():
        if known_artist in artist_lower or artist_lower in known_artist:
            tags.update(artist_tags)
    
    chord_info = analyze_chords(content)
    if chord_info['jazz-chords']:
        tags.add('jazz-chords')
    if chord_info['tab']:
        tags.add('tab')
    if chord_info['capo']:
        tags.add('capo')
    
    content_lower = content.lower()
    for word, tag in [
        ('rockabilly', 'rockabilly'), ('psychobilly', 'rockabilly'),
        ('swing', 'swing'), ('jive', 'swing'),
        ('ska', 'ska'), ('2 tone', 'ska'),
        ('punk', 'punk'), ('folk', 'folk'), ('traditional', 'folk'),
        ('blues', 'blues'), ('comedy', 'comedy'), ('humour', 'comedy'),
        ('christmas', 'christmas'), ('xmas', 'christmas'),
        ('disney', 'disney'), ('frozen', 'disney'),
        ('soundtrack', 'soundtrack'), ('film', 'soundtrack'),
        ('irish', 'irish'), ('celtic', 'irish'),
        ('country', 'country'), ('motown', 'motown'),
        ('grunge', 'grunge'), ('britpop', 'britpop'),
        ('indie', 'indie'), ('acoustic', 'acoustic'),
        ('instrumental', 'instrumental'), ('novelty', 'novelty'),
        ('neo-swing', 'swing-revival'), ('swing revival', 'swing-revival'),
    ]:
        if word in content_lower:
            tags.add(tag)
    
    for era in ['50s', '60s', '70s', '80s', '90s', '00s', '10s']:
        if era in content_lower:
            tags.add(era)
    
    artist_slug = re.sub(r'[^a-z0-9]+', '-', artist_lower).strip('-')
    if artist_slug and artist_slug != 'unknown':
        tags.add(artist_slug)
    
    return (filepath.name, title, artist, sorted(tags))

def main():
    files = sorted(CHARTS_DIR.glob('*.md'))
    suggestions = [suggest_tags_for_file(f) for f in files]
    
    all_tags = Counter()
    for _, _, _, tags in suggestions:
        all_tags.update(tags)
    
    print(f'Analyzed {len(suggestions)} files\n')
    print('Top 30 suggested tags:')
    for tag, count in all_tags.most_common(30):
        print(f'  {tag}: {count}')
    
    no_tags = sum(1 for _, _, _, tags in suggestions if not tags)
    print(f'\nFiles with no tags: {no_tags}')
    
    print('\n--- Sample suggestions (first 20) ---')
    for fname, title, artist, tags in suggestions[:20]:
        print(f'{fname}:')
        print(f'  Artist: {artist}')
        print(f'  Tags: {", ".join(tags) if tags else "(none)"}')
        print()
    
    if no_tags > 0:
        print(f'\n--- Files with no tags ({no_tags} total) ---')
        count = 0
        for fname, title, artist, tags in suggestions:
            if not tags:
                print(f'  {fname} (Artist: {artist})')
                count += 1
                if count >= 20:
                    print(f'  ... and {no_tags - 20} more')
                    break

if __name__ == '__main__':
    main()

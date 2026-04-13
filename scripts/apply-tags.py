#!/usr/bin/env python3
"""Apply suggested tags to all chart files."""
import re
from pathlib import Path
from collections import Counter

CHARTS_DIR = Path(__file__).resolve().parent.parent / "charts"

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
    'the proclaimers': ['folk-rock', '90s', 'scottish'],
    'caro emerald': ['swing', 'jazz', 'modern'],
    'meghan trainor': ['pop', 'modern'],
    'postmodern jukebox': ['swing', 'jazz', 'modern'],
    'etta james': ['blues', 'soul', 'r&b'],
    'blink-182': ['punk', 'pop-punk', '90s'],
    'lenny kravitz': ['rock', '90s', '00s'],
    'blondie': ['punk', 'new-wave', '70s', '80s'],
    'sam cooke': ['soul', 'r&b', '60s'],
    'erasure': ['synth-pop', '80s', 'new-wave'],
    'rihanna': ['pop', 'r&b', '00s'],
    'the baseballs': ['rockabilly', 'modern'],
    'sicknotes': ['comedy', 'modern', 'uk'],
    'the corrs': ['irish', 'pop', '90s'],
    'the cranberries': ['irish', '90s', 'alternative'],
    'van morrison': ['irish', 'soul', '60s'],
    'thin lizzy': ['irish', '70s', 'rock'],
    'u2': ['irish', '80s', 'rock'],
    'the undertones': ['irish', 'punk', '70s'],
    'the pogues': ['celtic-punk', 'folk', '80s'],
    'bellowhead': ['folk', 'traditional', 'english'],
    'the clash': ['punk', '70s', 'rock'],
    'the jam': ['punk', 'mod', '70s'],
    'paul weller': ['mod', 'rock', 'britpop'],
    'madness': ['ska', '2-tone', '80s'],
    'the specials': ['ska', '2-tone', '70s'],
    'bad manners': ['ska', '2-tone', '80s'],
    'the selecter': ['ska', '2-tone', '70s'],
    'the beat': ['ska', '2-tone', '70s'],
    'the english beat': ['ska', '2-tone', '70s'],
    'bob marley': ['reggae', '70s'],
    'toots and the maytals': ['reggae', 'ska', '60s'],
    'desmond dekker': ['reggae', 'ska', '60s'],
    'the wailers': ['reggae', '70s'],
    'sublime': ['ska', 'punk', '90s'],
    'no doubt': ['ska', 'pop', '90s'],
    'reel big fish': ['ska', 'punk', '90s'],
    'less than jake': ['ska', 'punk', '90s'],
    'operation ivy': ['ska', 'punk', '80s'],
    'rancid': ['punk', 'ska', '90s'],
    'the Mighty Mighty Bosstones': ['ska', 'punk', '90s'],
    'mighty mighty bosstones': ['ska', 'punk', '90s'],
    'the specials': ['ska', '2-tone', '70s'],
    'amy winehouse': ['soul', '00s', 'r&b'],
    'adele': ['pop', 'soul', 'modern'],
    'duffy': ['soul', '00s', 'welsh'],
    'joss stone': ['soul', '00s', 'r&b'],
    'paloma faith': ['soul', 'pop', 'modern'],
    'maroon 5': ['pop', 'rock', '00s'],
    'bruno mars': ['pop', 'funk', 'modern'],
    'justin timberlake': ['pop', 'r&b', '00s'],
    'michael jackson': ['pop', 'funk', '80s'],
    'prince': ['funk', 'pop', '80s'],
    'james brown': ['funk', 'soul', '60s'],
    'parliament': ['funk', '70s'],
    'funkadelic': ['funk', '70s'],
    'sly and the family stone': ['funk', 'soul', '60s'],
    'the meters': ['funk', 'soul', '60s'],
    'booker t': ['soul', 'funk', '60s'],
    'otis redding': ['soul', '60s'],
    'sam and dave': ['soul', '60s'],
    'percy sledge': ['soul', '60s'],
    'solomon burke': ['soul', '60s'],
    'ben e king': ['soul', '60s'],
    'the temptations': ['soul', 'motown', '60s'],
    'the supremes': ['soul', 'motown', '60s'],
    'marvin gaye': ['soul', 'motown', '70s'],
    'stevie wonder': ['soul', 'funk', '70s'],
    'the jackson 5': ['soul', 'motown', '70s'],
    'jackson 5': ['soul', 'motown', '70s'],
    'the isley brothers': ['soul', 'funk', '60s'],
    'isley brothers': ['soul', 'funk', '60s'],
    'the gap band': ['funk', '80s'],
    'gap band': ['funk', '80s'],
    'earth wind and fire': ['funk', 'soul', '70s'],
    'earth, wind & fire': ['funk', 'soul', '70s'],
    'kool & the gang': ['funk', 'disco', '70s'],
    'kool and the gang': ['funk', 'disco', '70s'],
    'chic': ['disco', 'funk', '70s'],
    'bee gees': ['disco', '70s', 'pop'],
    'donna summer': ['disco', '70s'],
    'gloria gaynor': ['disco', '70s'],
    'village people': ['disco', '70s'],
    'abba': ['disco', '70s', 'pop'],
    'the carpenters': ['pop', '70s'],
    'carpenters': ['pop', '70s'],
    'fleetwood mac': ['rock', '70s', 'pop'],
    'eagles': ['rock', '70s', 'country-rock'],
    'led zeppelin': ['rock', '70s', 'hard-rock'],
    'deep purple': ['rock', '70s', 'hard-rock'],
    'black sabbath': ['rock', '70s', 'heavy-metal'],
    'ac/dc': ['rock', '70s', 'hard-rock'],
    'aerosmith': ['rock', '70s', 'hard-rock'],
    'kiss': ['rock', '70s', 'glam-rock'],
    'david bowie': ['glam-rock', '70s', 'rock'],
    't rex': ['glam-rock', '70s'],
    'marc bolan': ['glam-rock', '70s'],
    'roxy music': ['glam-rock', '70s'],
    'bryan ferry': ['glam-rock', '70s'],
    'lou reed': ['glam-rock', '70s'],
    'iggy pop': ['punk', 'glam-rock', '70s'],
    'the stooges': ['punk', 'garage-rock', '60s'],
    'mc5': ['punk', 'garage-rock', '60s'],
    'the velvet underground': ['rock', '60s', 'psychedelic'],
    'velvet underground': ['rock', '60s', 'psychedelic'],
    'the byrds': ['folk-rock', '60s'],
    'byrds': ['folk-rock', '60s'],
    'crosby stills & nash': ['folk-rock', '60s'],
    'crosby, stills & nash': ['folk-rock', '60s'],
    'crosby stills nash & young': ['folk-rock', '60s'],
    'neil young': ['folk-rock', '70s', 'singer-songwriter'],
    'joni mitchell': ['folk', 'singer-songwriter', '70s'],
    'leonard cohen': ['folk', 'singer-songwriter', '60s'],
    'paul simon': ['folk', 'singer-songwriter', '70s'],
    'art garfunkel': ['folk', 'singer-songwriter', '70s'],
    'james taylor': ['folk', 'singer-songwriter', '70s'],
    'carole king': ['folk', 'singer-songwriter', '70s'],
    'jackson browne': ['folk-rock', '70s', 'singer-songwriter'],
    'warren zevon': ['rock', '70s', 'singer-songwriter'],
    'tom petty': ['rock', '70s', 'heartland-rock'],
    'tom petty & the heartbreakers': ['rock', '70s', 'heartland-rock'],
    'bruce springsteen': ['rock', '70s', 'heartland-rock'],
    'john mellencamp': ['rock', '80s', 'heartland-rock'],
    'bob seger': ['rock', '70s', 'heartland-rock'],
    'steve earle': ['country', 'rock', 'americana'],
    'dwight yoakam': ['country', 'rockabilly', '80s'],
    'marty stuart': ['country', 'bluegrass'],
    'ricky skaggs': ['bluegrass', 'country'],
    'alison krauss': ['bluegrass', 'country'],
    'gillian welch': ['americana', 'folk'],
    'dave rawlings': ['americana', 'folk'],
    'ryan adams': ['americana', 'rock', '00s'],
    'whiskeytown': ['americana', '90s'],
    'the avett brothers': ['americana', 'folk', 'modern'],
    'mumford & sons': ['folk-rock', 'modern'],
    'mumford and sons': ['folk-rock', 'modern'],
    'the lumineers': ['folk-rock', 'modern'],
    'of monsters and men': ['folk-rock', 'modern'],
    'the head and the heart': ['folk-rock', 'modern'],
    'fleet foxes': ['folk-rock', 'indie', '00s'],
    'bon iver': ['indie', 'folk', 'modern'],
    'iron & wine': ['indie', 'folk', 'modern'],
    'iron and wine': ['indie', 'folk', 'modern'],
    'ray lamontagne': ['folk', 'soul', 'modern'],
    'amos lee': ['folk', 'soul', 'modern'],
    'gregory alan isakov': ['folk', 'indie', 'modern'],
    'the decemberists': ['indie', 'folk', 'modern'],
    'the shins': ['indie', '00s'],
    'arcade fire': ['indie', '00s'],
    'the national': ['indie', '00s'],
    'interpol': ['indie', '00s'],
    'the strokes': ['indie', '00s', 'garage-rock'],
    'the whites stripes': ['garage-rock', '00s'],
    'the white stripes': ['garage-rock', '00s'],
    'the hives': ['garage-rock', '00s'],
    'the von bondies': ['garage-rock', '00s'],
    'the libertines': ['indie', '00s', 'garage-rock'],
    'babyshambles': ['indie', '00s', 'garage-rock'],
    'the kooks': ['indie', '00s', 'britpop'],
    'razorlight': ['indie', '00s', 'garage-rock'],
    'the fratellis': ['indie', '00s', 'garage-rock'],
    'the view': ['indie', '00s', 'rock'],
    'arctic monkeys': ['indie', '00s', 'rock'],
    'miles kane': ['indie', '10s', 'rock'],
    'the last shadow puppets': ['indie', '00s', 'baroque-pop'],
    'alex turner': ['indie', '00s', 'rock'],
    'the coral': ['indie', '00s', 'psychedelic'],
    'the zutons': ['indie', '00s', 'rock'],
    'shed seven': ['britpop', '90s', 'rock'],
    'cast': ['britpop', '90s', 'rock'],
    'ocean colour scene': ['britpop', '90s', 'rock'],
    'supergrass': ['britpop', '90s', 'rock'],
    'blur': ['britpop', '90s', 'rock'],
    'pulp': ['britpop', '90s', 'rock'],
    'suede': ['britpop', '90s', 'rock'],
    'elastica': ['britpop', '90s', 'rock'],
    'sleeper': ['britpop', '90s', 'rock'],
    'echobelly': ['britpop', '90s', 'rock'],
    'dodgy': ['britpop', '90s', 'rock'],
    'gene': ['britpop', '90s', 'rock'],
    'longpigs': ['britpop', '90s', 'rock'],
    'boothill foot tappers': ['folk-rock', '80s', 'novelty'],
    'show of hands': ['folk', 'english', 'modern'],
    'steve knightley': ['folk', 'english', 'modern'],
    'phil beer': ['folk', 'english', 'modern'],
    'the levellers': ['folk-rock', '90s', 'celtic'],
    'flogging molly': ['celtic-punk', 'folk', '90s'],
    'dropkick murphys': ['celtic-punk', 'folk', '90s'],
    'the real mckenzies': ['celtic-punk', 'folk', '90s'],
    'the rumjacks': ['celtic-punk', 'folk', 'modern'],
    'the clancy brothers': ['irish', 'folk', 'traditional'],
    'the dubliners': ['irish', 'folk', 'traditional'],
    'the chieftains': ['irish', 'folk', 'traditional'],
    'snow patrol': ['irish', '00s', 'alternative'],
    'stiff little fingers': ['irish', 'punk', '70s'],
    'the boomtown rats': ['irish', 'punk', '70s'],
    'bob geldof': ['irish', 'punk', '80s'],
    'sinead oconnor': ['irish', 'pop', '80s'],
    'enya': ['irish', 'new-age', '80s'],
    'andrea corr': ['irish', 'pop', '00s'],
    'damien rice': ['irish', 'indie', '00s'],
    'glen hansard': ['irish', 'indie', '00s'],
    'the frames': ['irish', 'indie', '90s'],
    'the script': ['irish', 'pop', '00s'],
    'westlife': ['irish', 'pop', '90s'],
    'boyzone': ['irish', 'pop', '90s'],
    'ronan keating': ['irish', 'pop', '90s'],
    'ash': ['irish', 'britpop', '90s'],
    'therapy': ['irish', 'alternative', '90s'],
    'the undertones': ['irish', 'punk', '70s'],
    'the bogues': ['irish', 'punk', '70s'],
    'the bogues': ['irish', 'punk', '70s'],
    'the bogues': ['irish', 'punk', '70s'],
}

def analyze_chords(content):
    chords = set(re.findall(r'\[([^\]]+)\]', content))
    has_jazz = any(re.search(r'(maj7|m7|dim|aug|9|11|13|sus|add)', c) for c in chords)
    has_capo = 'capo' in content.lower()
    has_tab = '```text' in content
    return {'jazz-chords': has_jazz, 'capo': has_capo, 'tab': has_tab}

def suggest_tags(filepath):
    content = filepath.read_text(encoding='utf-8')
    artist_m = re.search(r'^## (.+)$', content, re.MULTILINE)
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
    
    return sorted(tags)

def main():
    files = sorted(CHARTS_DIR.glob('*.md'))
    updated = 0
    
    for filepath in files:
        content = filepath.read_text(encoding='utf-8')
        tags = suggest_tags(filepath)
        
        if not tags:
            continue
        
        # Build new tags line
        tags_str = ', '.join(tags)
        new_tags_line = f'tags: [{tags_str}]'
        
        # Replace existing tags line
        new_content = re.sub(
            r'^tags:\s*\[.*\]$',
            new_tags_line,
            content,
            count=1,
            flags=re.MULTILINE
        )
        
        if new_content != content:
            filepath.write_text(new_content, encoding='utf-8')
            updated += 1
    
    print(f'Updated tags for {updated} files')
    
    # Verify
    no_tags = 0
    for f in files:
        content = f.read_text(encoding='utf-8')
        tags_m = re.search(r'^tags:\s*\[(.*)\]$', content, re.MULTILINE)
        if tags_m and tags_m.group(1).strip():
            pass
        else:
            no_tags += 1
    
    print(f'Files still with no tags: {no_tags}')

if __name__ == '__main__':
    main()

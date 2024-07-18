import requests
import sqlite3


id = 277823
ABILITIES = ['str', 'dex', 'con', 'int', 'wis', 'cha']
MODIFIERS = {
            1: -5, 2: -4, 3: -4, 4: -3, 5: -3, 6: -2, 7: -2, 8: -1, 9: -1, 10: 0, 11: 0, 12: 1, 13: 1, 14: 2, 15: 2, 
            16: 3, 17: 3, 18: 4, 19: 4, 20: 5, 21: 5, 22: 6, 23: 6, 24: 7, 25: 7, 26: 8, 27: 8, 28: 9, 29: 9
            }
PROFICIENCIES = [
                'perception', 'fortitude', 'reflex', 'will', 'acrobatics', 'arcana', 'athletics', 'crafting', 'deception', 'diplomacy',
                'intimidation', 'medicine', 'nature', 'occultism', 'performance', 'religion', 'society', 'stealth', 'survival', 'thievery'
                ]
PROFICIENCY_BASE = {
                    'perception': 'wis', 'fortitude': 'con', 'reflex': 'dex', 'will': 'wis', 'acrobatics': 'dex', 'arcana': 'int', 'athletics': 'str',
                    'crafting': 'int', 'deception': 'cha', 'diplomacy': 'cha', 'intimidation': 'cha', 'medicine': 'wis', 'nature': 'wis', 'occultism': 'int',
                    'performance': 'cha', 'religion': 'wis', 'society': 'int', 'stealth': 'dex', 'survival': 'wis', 'thievery': 'dex'
                    }


def get_character(id):

    character = {}

    url = 'https://pathbuilder2e.com/json.php?id=%s' % id

    headers = {
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36',
                }

    data = requests.get(url=url, headers=headers)

    data = dict(data.json())['build']

    basics = {
              'name': data['name'],'level': data['level'], 'ancestry': data['ancestry'], 'class': data['class'], 
              'background': data['background'], 'AC': data['acTotal']['acTotal']
              }

    character.update(basics)

    c_abilities = {}
    
    for i in ABILITIES:
        a = data['abilities'][i]
        item = {i: a, i + 'Mod': MODIFIERS[a]}
        c_abilities.update(item)

    character.update(c_abilities)

    c_proficiencies = {}

    for i in PROFICIENCIES:
        p = data['proficiencies'][i]
        match p:
            case 0:
                training = 'u'
            case 2:
                training = 't'
            case 4:
                training = 'e'
            case 6:
                training = 'm'
            case 8:
                training = 'l'
        if p > 0:
            p += data['level']
        base = PROFICIENCY_BASE[i] + 'Mod'
        p += c_abilities[base]
        item = {i: p, i + 'Train': training}
        c_proficiencies.update(item)

    character.update(c_proficiencies)

    lores = {}

    for i in range(len(data['lores'])):
        k = data['lores'][i][0]
        v = data['lores'][i][1]
        match v:
            case 0:
                training = 'u'
            case 2:
                training = 't'
            case 4:
                training = 'e'
            case 6:
                training = 'm'
            case 8:
                training = 'l'
        v += data['level'] + c_abilities['intMod']
        item = {'lore_'+k: v, 'lore_'+k+'Train': training}
        lores.update(item)

    character.update(lores)

    return character



def update_db(db, id=277823, overwrite=False):

    columns = db.execute(
        "SELECT c.name FROM pragma_table_info('characters') c;"
    ).fetchall()
    columns = [k[0] for k in columns]

    print(id)
    character = get_character(id)
    unknown = {}
    for key in character:
        if key not in columns:
            unknown.update({key: character[key]})
    
    def append_db(conn, new):
        for i in new:
            if type(new[i]) == int:
                conn.execute('ALTER TABLE characters ADD COLUMN '+i+' INT')
            elif type(new[i]) == str:
                conn.execute('ALTER TABLE characters ADD COLUMN '+i+' VARCHAR')
            

    def post_row(conn, rec, overwrite=False):
        if overwrite:
            conn.execute('DELETE FROM characters WHERE name 0 '+rec['name']+';')
            conn.commit()
        try:
            keys = ', '.join(rec.keys())
            question_marks = ', '.join(list('?'*len(rec)))
            values = tuple(rec.values())
            conn.execute('INSERT INTO characters ('+keys+') VALUES ('+question_marks+')', values)
            conn.commit()
        except sqlite3.IntegrityError:
            pass


    append_db(db, unknown)
    post_row(db, character, overwrite)




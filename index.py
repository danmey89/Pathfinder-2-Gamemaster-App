from flask import render_template, Blueprint, request, jsonify
from db import get_db
from data_handling import update_db, PROFICIENCIES

bp = Blueprint('index', __name__)


@bp.route('/')
def index():
    db = get_db()

    stats = db.execute('SELECT * FROM characters;').fetchall()
    stats = [k for k in stats]

    columns = stats[0].keys()

    stat_list = {}
    names = []

    for row in range(len(stats)):
        character = {}
        for i in range(len(columns)):
            item = {columns[i]: stats[row][i]}
            character.update(item)
        stat_list.update({character['name']:character})
        names.append(character['name'])
    

    lores = db.execute("SELECT name FROM pragma_table_info('characters') WHERE Name LIKE 'lore%' AND Name NOT LIKE '%rain';")
    lores = [k[0] for k in lores]

    return render_template('index.html', stat_list=stat_list, lores=lores, proficiencies=PROFICIENCIES, names=names)


@bp.route('/load', methods=['POST'])
def load():
    f_id = request.form['f_id']
    update_db(db=get_db(), id=f_id)

    return '', 204


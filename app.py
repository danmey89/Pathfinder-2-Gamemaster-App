from flask import Flask
import os
import db, index

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        DATABASE = os.path.join(app.instance_path, 'pf2_gm.sqlite')
    )

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)

    app.register_blueprint(index.bp)

    return app
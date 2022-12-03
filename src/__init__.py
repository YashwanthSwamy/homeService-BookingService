from flask import Flask
from .externalServices.database import tables
from .externalServices.database.services.database import Database


def create_app(config):
    print("CREATED APP INSTANCE!!\n\n")
    app = Flask(__name__)
    app.config.from_object(config)
    Database.init_app(app)
    tables.init_app()

    return app

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from flask import Flask
from contextlib import contextmanager
from src.services.decorators import bind_app_context


class App:
    """
    current Flask application instance wrapper
    """

    _app: Flask or None = None

    @classmethod
    def set_app(cls, app: Flask):
        cls._app = app

    @classmethod
    def get_app(cls) -> Flask:
        if cls._app is None:
            print("[DB] trying to access app before init!")
        return cls._app


class Database:
    """
    current database instance wrapper
    """

    _dbi: SQLAlchemy or None = None
    _session: scoped_session or None = None

    @classmethod
    def init_app(cls, app: Flask):
        App.set_app(app)
        cls.init_db()

    @classmethod
    @contextmanager
    def session_manager(cls):
        # get the resource
        try:
            session = cls.get_session()
            yield session
            session.commit()
            session.flush()

        except Exception as generic_error:
            print(f"[session-manager]{generic_error}")
            session.rollback()
            raise generic_error

    @classmethod
    def init_db(cls) -> SQLAlchemy:
        """ This method is responsible for initializing the database within
        the app context """

        print("[DB] initializing database")
        app = App.get_app()
        with app.app_context():
            db = cls.get_db()
            app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
            app.config['DB_INIT_OK'] = True
            db.init_app(App.get_app())
            session_factory = sessionmaker(bind=cls.get_engine())
            cls._session = scoped_session(session_factory)
            cls.init_tables(db)
            return db

    @staticmethod
    def init_tables(db):
        """ This method creates all the tables """
        print("[DB] init tables method called")
        db.create_all()
        db.session.commit()

    @classmethod
    def get_db(cls) -> SQLAlchemy:
        """ This method returns the database instance if it already
        exists, else will create a new SQLAlchemy object """

        if cls._dbi is not None:
            return cls._dbi
        else:
            cls._dbi = SQLAlchemy()
            return cls._dbi

    @classmethod
    def get_engine(cls) -> Engine:
        return cls.get_db().get_engine()

    @classmethod
    @bind_app_context(app_getter=App.get_app)
    def get_session(cls) -> scoped_session:
        """creates a new scoped session which will be maintained per application thread
        via threading.local() and returns the same session object
        for more ref:
        https://docs.sqlalchemy.org/en/14/orm/contextual.html
        https://docs.sqlalchemy.org/en/14/orm/contextual.html#thread-local-scope"""

        if cls._session is None:
            session_factory = sessionmaker(bind=cls.get_engine())
            cls._session = scoped_session(session_factory)
        return cls._session

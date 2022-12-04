from . import configRoutes


def init_app(app):
    configRoutes.load_config_routes(app)

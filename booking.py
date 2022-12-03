from config import DevelopmentConfig
from src import create_app

app = create_app(DevelopmentConfig)


def run():
    app.run(
        port=app.config.get("PORT", 8080),
        host=app.config.get("HOST", "0.0.0.0"),
        use_reloader=False
    )


if __name__ == '__main__':
    run()

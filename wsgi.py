from app.core.app_factory import create_app

application = create_app()

if __name__ == "__main__":
    application.run()

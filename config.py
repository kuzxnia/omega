import os

postgres_local_base = "p ostgresql://rollie:rollie@127.0.0.1:5432/rollie"


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "my_precious_secret_key")
    DEBUG = False

    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:postgres@localhost/omega"

    # Flask-Restplus settings
    RESTPLUS_SWAGGER_UI_DOC_EXPANSION = "list"
    RESTPLUS_VALIDATE = True
    RESTPLUS_MASK_SWAGGER = False
    RESTPLUS_ERROR_404_HELP = False


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True


class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProductionConfig(Config):
    DEBUG = False


config_by_name = dict(dev=DevelopmentConfig, test=TestingConfig, prod=ProductionConfig)

key = Config.SECRET_KEY

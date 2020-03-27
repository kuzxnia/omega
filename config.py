import os

postgres_local_base = os.getenv(
    "postgres_uri", "postgresql://omega:omega@localhost/omega"
)


class Config:
    from omega.util.proxy.pool import FreeProxyPool
    SECRET_KEY = os.getenv("SECRET_KEY", "my_precious_secret_key")
    DEBUG = False

    SQLALCHEMY_DATABASE_URI = postgres_local_base

    # Flask-Restplus settings
    RESTPLUS_SWAGGER_UI_DOC_EXPANSION = "list"
    RESTPLUS_VALIDATE = True
    RESTPLUS_MASK_SWAGGER = False
    RESTPLUS_ERROR_404_HELP = False
    PROXY_POOL = 'FREE'  # FreeProxyPool


class DevelopmentConfig(Config):
    from omega.util.proxy.pool import DelayWithoutProxy
    ENV = "development"
    DEBUG = True
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    PROXY_POOL = 'DELAY'  # DelayWithoutProxy


class TestingConfig(Config):
    DEBUG = True
    TESTING = True
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProductionConfig(Config):
    pass


config_by_name = dict(dev=DevelopmentConfig, test=TestingConfig, prod=ProductionConfig)

key = Config.SECRET_KEY

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application configuration loaded from environment variables.

    Attributes:
        database_url (str): SQLAlchemy database connection URL.
        secret_key (str): Secret key used for signing JWT tokens.
        algorithm (str): JWT signing algorithm. Defaults to HS256.
        access_token_expire_minutes (int): JWT expiry in minutes. Defaults to 30.
    """

    database_url: str = "sqlite:///./shopease.db"
    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    credit_card_max_amount: float = 10_000.0
    paypal_max_amount: float = 5_000.0

    model_config = {"env_file": ".env"}


settings = Settings()

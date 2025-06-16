from pydantic_settings import BaseSettings


class Configs(BaseSettings):
    DB_ENGINE: str
    DB_USER: str
    DB_PW: str
    DB_HOST: str
    DB_PORT: str
    DATA_BASE: str

    @property
    def DATABASE_URL(self):
        return f"{self.DB_ENGINE}://{self.DB_USER}:{self.DB_PW}@{self.DB_HOST}:{self.DB_PORT}/{self.DATA_BASE}"

    KAKAO_API_KEY: str
    KAKAO_REDIRECT_URI: str

    SECRET_KEY: str
    REFRESH_SECRET_KEY: str
    ALGORITHM: str

    GOOGLE_CREDENTIAL: str

    class Config:
        env_file = ".env.test"

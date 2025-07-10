from pydantic_settings import BaseSettings


class Configs(BaseSettings):
    DB_ENGINE: str
    DB_USER: str
    DB_PW: str
    DB_HOST: str
    DB_PORT: str
    DATA_BASE: str

    # ====================== KAKAKO AUTH
    KAKAO_API_KEY: str
    KAKAO_REDIRECT_URI: str

    # ====================== AUTH
    SECRET_KEY: str
    REFRESH_SECRET_KEY: str
    ALGORITHM: str

    # ====================== 한국관광공사
    REQ_URL_DOMAIN: str
    ENC_TOUR_SECRET_KEY: str
    ORG_TOUR_SECRET_KEY: str

    # ====================== GCP AI VISION
    GOOGLE_CREDENTIAL: str

    # ====================== GCP CI/CD
    GCP_RUN_PROJECT_ID: str
    GCP_SA_EMAIL: str
    GCP_WIF_PROVIDER: str

    @property
    # def DATABASE_URL(self):
    #     return "postgresql+psycopg2://kimjihan77:dkffkqbd2019!@34.47.117.55:5432/bread"
    def DATABASE_URL(self):
        return f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PW}@/{self.DATA_BASE}?host=/cloudsql/{self.GCP_RUN_PROJECT_ID}:asia-northeast3:bread-db"

    class Config:
        env_file = ".env"

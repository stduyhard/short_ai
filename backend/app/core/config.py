from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "short-video-backend"


settings = Settings()

import os
from typing import Literal


EngineMode = Literal["python", "simpleengine", "external"]


class Settings:
    def __init__(self) -> None:
        self.ENGINE_MODE: EngineMode = os.getenv("BF_ENGINE_MODE", "python")  # python|simpleengine|external
        self.STOCKFISH_PATH: str | None = os.getenv("BF_STOCKFISH_PATH")
        self.EXTERNAL_ENGINE_URL: str | None = os.getenv("BF_EXTERNAL_ENGINE_URL")
        self.LOG_LEVEL: str = os.getenv("BF_LOG_LEVEL", "info")
        self.ALLOW_CORS: bool = os.getenv("BF_ALLOW_CORS", "true").lower() == "true"
        self.ENGINE_POOL_SIZE: int = int(os.getenv("BF_ENGINE_POOL_SIZE", "1"))
        self.CACHE_ENABLED: bool = os.getenv("BF_CACHE_ENABLED", "false").lower() == "true"


settings = Settings()

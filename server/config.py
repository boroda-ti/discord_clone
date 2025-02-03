import os

class BaseConfig:

    @staticmethod
    def get(key: str) -> any:
        return os.getenv(key)
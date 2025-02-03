def create_url(user: str, password: str, host: str, port: str, dbname: str) -> str:
    return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{dbname}"
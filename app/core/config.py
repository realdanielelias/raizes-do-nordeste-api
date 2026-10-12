import os

PROJECT_NAME = os.getenv("PROJECT_NAME", "Raízes do Nordeste API")
SECRET_KEY = os.getenv("SECRET_KEY", "chave_secreta_jwt_raizes_nordeste_2026_segura")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./raizes_nordeste.db")
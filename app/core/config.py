import os
import logging
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env (na raiz do projeto) para o ambiente.
# Variáveis já exportadas no sistema têm prioridade sobre o .env.
load_dotenv()

logger = logging.getLogger("uvicorn.error")

# Chave usada apenas quando SECRET_KEY não está definida (ambiente de desenvolvimento).
_DEV_SECRET_KEY = "chave_insegura_apenas_para_desenvolvimento"

PROJECT_NAME = os.getenv("PROJECT_NAME", "Raízes do Nordeste - API Back-End")
SECRET_KEY = os.getenv("SECRET_KEY") or ""
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./raizes_nordeste.db")

if not SECRET_KEY:
    SECRET_KEY = _DEV_SECRET_KEY
    logger.warning(
        "SECRET_KEY não definida! Usando chave padrão INSEGURA de desenvolvimento. "
        "Crie o arquivo .env (cp .env.example .env) e defina uma SECRET_KEY própria."
    )
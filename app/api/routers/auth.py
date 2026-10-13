from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.infrastructure.database import get_db
from app.api.schemas import LoginRequest, LoginResponse
from app.application.services import AuthService

router = APIRouter(prefix="/auth", tags=["Autenticação"])

@router.post("/login", response_model=LoginResponse, summary="Autenticar usuário")
def login(dados: LoginRequest, db: Session = Depends(get_db)):
    return AuthService.autenticar(db, dados.email, dados.senha)
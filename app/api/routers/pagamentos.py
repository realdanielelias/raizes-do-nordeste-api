from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.infrastructure.database import get_db
from app.api.schemas import PagamentoMockRequest, PagamentoMockResponse
from app.application.services import PaymentMockService
from app.core.security import obter_usuario_logado

router = APIRouter(prefix="/pagamentos", tags=["Pagamentos Mock"])

@router.post("/mock", response_model=PagamentoMockResponse, summary="Processar pagamento externo simulado")
def pagar_mock(
    dados: PagamentoMockRequest,
    db: Session = Depends(get_db),
    usuario: dict = Depends(obter_usuario_logado)
):
    return PaymentMockService.processar_mock(db, dados, usuario_id=usuario["id"])
from datetime import datetime, timezone
from typing import List, Optional, Any
from pydantic import BaseModel, EmailStr, Field
from app.domain.enums import CanalPedido, StatusPedido, MetodoPagamento
from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES

class ErrorDetail(BaseModel):
    field: str
    issue: str

class ErrorResponse(BaseModel):
    error: str
    message: str
    details: List[ErrorDetail] = []
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    path: str

class LoginRequest(BaseModel):
    email: EmailStr
    senha: str

class UserInfo(BaseModel):
    id: int
    nome: str
    perfil: str

class LoginResponse(BaseModel):
    accessToken: str
    tokenType: str = "Bearer"
    expiresIn: int = ACCESS_TOKEN_EXPIRE_MINUTES * 60
    user: UserInfo

class ProdutoResponse(BaseModel):
    id: int
    nome: str
    descricao: Optional[str]
    preco: float
    categoria: str
    quantidadeDisponivel: int

class ItemPedidoCreate(BaseModel):
    produtoId: int
    quantidade: int = Field(gt=0, description="Quantidade deve ser maior que zero")

class PedidoCreate(BaseModel):
    unidadeId: int
    canalPedido: CanalPedido
    formaPagamento: MetodoPagamento
    itens: List[ItemPedidoCreate] = Field(min_length=1, description="Ao menos um item no pedido")

class ItemPedidoResponse(BaseModel):
    produtoId: int
    quantidade: int
    precoUnitario: float
    subtotal: float

class PedidoResponse(BaseModel):
    pedidoId: int
    unidadeId: int
    canalPedido: str
    status: str
    valorTotal: float
    itens: List[ItemPedidoResponse]
    criadoEm: datetime

class PagamentoMockRequest(BaseModel):
    pedidoId: int
    metodo: MetodoPagamento
    simularAprovacao: bool = True

class PagamentoMockResponse(BaseModel):
    transacaoId: str
    pedidoId: int
    statusPagamento: str
    novoStatusPedido: str
    mensagem: str

class StatusUpdateRequest(BaseModel):
    novoStatus: StatusPedido
from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.infrastructure.database import get_db
from app.infrastructure.models import PedidoDB
from app.api.schemas import PedidoCreate, PedidoResponse, ItemPedidoResponse, StatusUpdateRequest
from app.application.services import OrderService
from app.core.security import obter_usuario_logado, exigir_perfil

router = APIRouter(prefix="/pedidos", tags=["Pedidos"])

@router.post("", response_model=PedidoResponse, status_code=status.HTTP_201_CREATED, summary="Criar pedido multicanal")
def criar_pedido(
    dados: PedidoCreate,
    db: Session = Depends(get_db),
    usuario: dict = Depends(obter_usuario_logado)
):
    pedido_db = OrderService.criar_pedido(db, dados, usuario_id=usuario["id"])
    return PedidoResponse(
        pedidoId=pedido_db.id,
        unidadeId=pedido_db.unidade_id,
        canalPedido=pedido_db.canal_pedido,
        status=pedido_db.status,
        valorTotal=pedido_db.valor_total,
        itens=[
            ItemPedidoResponse(
                produtoId=it.produto_id,
                quantidade=it.quantidade,
                precoUnitario=it.preco_unitario,
                subtotal=it.subtotal
            ) for it in pedido_db.itens
        ],
        criadoEm=pedido_db.criado_em
    )

@router.get("", response_model=List[PedidoResponse], summary="Listar e filtrar pedidos")
def listar_pedidos(
    canalPedido: Optional[str] = Query(None, description="Filtro obrigatório de multicanalidade (APP, TOTEM...)"),
    status: Optional[str] = Query(None, description="Filtro por status"),
    db: Session = Depends(get_db),
    usuario: dict = Depends(obter_usuario_logado)
):
    query = db.query(PedidoDB)
    if canalPedido:
        query = query.filter(PedidoDB.canal_pedido == canalPedido.upper())
    if status:
        query = query.filter(PedidoDB.status == status.upper())
    pedidos = query.all()

    return [
        PedidoResponse(
            pedidoId=p.id,
            unidadeId=p.unidade_id,
            canalPedido=p.canal_pedido,
            status=p.status,
            valorTotal=p.valor_total,
            itens=[
                ItemPedidoResponse(
                    produtoId=it.produto_id,
                    quantidade=it.quantidade,
                    precoUnitario=it.preco_unitario,
                    subtotal=it.subtotal
                ) for it in p.itens
            ],
            criadoEm=p.criado_em
        ) for p in pedidos
    ]

@router.patch("/{id}/status", summary="Atualizar status do pedido (Cozinha/Operação)")
def atualizar_status(
    id: int,
    dados: StatusUpdateRequest,
    db: Session = Depends(get_db),
    usuario: dict = Depends(exigir_perfil(["ATENDENTE", "GERENTE"]))
):
    pedido = db.query(PedidoDB).filter(PedidoDB.id == id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail={"error": "NAO_ENCONTRADO", "message": "Pedido inexistente"})
    pedido.status = dados.novoStatus.value
    db.commit()
    return {"pedidoId": id, "statusAtualizado": pedido.status}
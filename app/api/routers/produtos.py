from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from app.infrastructure.database import get_db
from app.infrastructure.models import EstoqueDB, ProdutoDB
from app.api.schemas import ProdutoResponse

router = APIRouter(prefix="/produtos", tags=["Produtos e Cardápio"])

@router.get("", response_model=List[ProdutoResponse], summary="Consultar cardápio da unidade")
def listar_produtos_por_unidade(
    unidadeId: int = Query(..., description="ID da franquia para consulta de estoque"),
    db: Session = Depends(get_db)
):
    estoques = db.query(EstoqueDB).join(ProdutoDB).filter(
        EstoqueDB.unidade_id == unidadeId,
        ProdutoDB.ativo == True
    ).all()
    
    return [
        ProdutoResponse(
            id=item.produto.id,
            nome=item.produto.nome,
            descricao=item.produto.descricao,
            preco=item.produto.preco,
            categoria=item.produto.categoria,
            quantidadeDisponivel=item.quantidade_disponivel
        )
        for item in estoques
    ]
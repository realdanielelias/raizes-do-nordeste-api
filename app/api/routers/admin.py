import json
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from app.infrastructure.database import get_db
from app.infrastructure.models import EstoqueDB, UnidadeDB, ProdutoDB, AuditoriaLogDB
from app.core.security import exigir_perfil

router = APIRouter(prefix="/unidades/estoque", tags=["Gestão Administrativa de Franquias"])

class AjusteEstoqueSchema(BaseModel):
    unidadeId: int
    produtoId: int
    novaQuantidade: int = Field(ge=0, description="Quantidade deve ser maior ou igual a zero")

@router.post("/ajuste", summary="Ajuste manual de estoque (Exclusivo Gerente)")
def ajustar_estoque(
    dados: AjusteEstoqueSchema,
    db: Session = Depends(get_db),
    usuario: dict = Depends(exigir_perfil(["GERENTE"]))
):
    unidade = db.query(UnidadeDB).filter(UnidadeDB.id == dados.unidadeId, UnidadeDB.ativo == True).first()
    if not unidade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "UNIDADE_NAO_ENCONTRADA", "message": f"Unidade {dados.unidadeId} não encontrada ou inativa."}
        )

    produto = db.query(ProdutoDB).filter(ProdutoDB.id == dados.produtoId, ProdutoDB.ativo == True).first()
    if not produto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "PRODUTO_NAO_ENCONTRADO", "message": f"Produto ID {dados.produtoId} não encontrado ou inativo."}
        )

    estoque = db.query(EstoqueDB).filter(
        EstoqueDB.unidade_id == dados.unidadeId,
        EstoqueDB.produto_id == dados.produtoId
    ).first()

    qtd_anterior = estoque.quantidade_disponivel if estoque else 0

    if not estoque:
        estoque = EstoqueDB(
            unidade_id=dados.unidadeId,
            produto_id=dados.produtoId,
            quantidade_disponivel=dados.novaQuantidade,
            atualizado_em=datetime.now(timezone.utc)
        )
        db.add(estoque)
    else:
        estoque.quantidade_disponivel = dados.novaQuantidade
        estoque.atualizado_em = datetime.now(timezone.utc)

    db.add(AuditoriaLogDB(
        usuario_id=usuario["id"],
        acao="AJUSTE_MANUAL_ESTOQUE",
        entidade="ESTOQUE",
        registro_id=estoque.id if estoque.id else 0,
        detalhes_json=json.dumps({
            "unidadeId": dados.unidadeId,
            "produtoId": dados.produtoId,
            "quantidadeAnterior": qtd_anterior,
            "novaQuantidade": dados.novaQuantidade
        })
    ))

    db.commit()

    return {
        "message": "Ajuste de estoque efetuado pelo Gerente com sucesso.",
        "dados": dados
    }
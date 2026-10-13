from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.core.security import exigir_perfil

router = APIRouter(prefix="/unidades/estoque", tags=["Gestão Administrativa de Franquias"])

class AjusteEstoqueSchema(BaseModel):
    unidadeId: int
    produtoId: int
    novaQuantidade: int

@router.post("/ajuste", summary="Ajuste manual de estoque (Exclusivo Gerente)")
def ajustar_estoque(
    dados: AjusteEstoqueSchema,
    usuario: dict = Depends(exigir_perfil(["GERENTE"]))
):
    return {"message": "Ajuste de estoque efetuado pelo Gerente com sucesso.", "dados": dados}
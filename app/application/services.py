import uuid
import json
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.infrastructure.models import (
    UsuarioDB, UnidadeDB, ProdutoDB, EstoqueDB, PedidoDB, ItemPedidoDB, PagamentoDB, AuditoriaLogDB
)
from app.api.schemas import PedidoCreate, PagamentoMockRequest
from app.core.security import hash_senha, verificar_senha, criar_token_jwt
from app.core.config import ACCESS_TOKEN_EXPIRE_MINUTES

class AuthService:
    @staticmethod
    def autenticar(db: Session, email: str, senha: str):
        usuario = db.query(UsuarioDB).filter(UsuarioDB.email == email).first()
        if not usuario or not verificar_senha(senha, usuario.senha_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"error": "CREDENCIAIS_INVALIDAS", "message": "E-mail ou senha incorretos."}
            )
        token = criar_token_jwt({"id": usuario.id, "email": usuario.email, "perfil": usuario.perfil})
        return {
            "accessToken": token,
            "tokenType": "Bearer",
            "expiresIn": ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user": {"id": usuario.id, "nome": usuario.nome, "perfil": usuario.perfil}
        }

class OrderService:
    @staticmethod
    def criar_pedido(db: Session, dados: PedidoCreate, usuario_id: int):
        unidade = db.query(UnidadeDB).filter(UnidadeDB.id == dados.unidadeId, UnidadeDB.ativo == True).first()
        if not unidade:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "UNIDADE_NAO_ENCONTRADA", "message": f"Unidade {dados.unidadeId} não encontrada ou inativa."}
            )

        valor_total = 0.0
        itens_a_inserir = []

        for item_in in dados.itens:
            produto = db.query(ProdutoDB).filter(ProdutoDB.id == item_in.produtoId, ProdutoDB.ativo == True).first()
            if not produto:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={"error": "PRODUTO_NAO_ENCONTRADO", "message": f"Produto ID {item_in.produtoId} não encontrado."}
                )

            estoque = db.query(EstoqueDB).filter(
                EstoqueDB.unidade_id == dados.unidadeId,
                EstoqueDB.produto_id == item_in.produtoId
            ).first()

            if not estoque or estoque.quantidade_disponivel < item_in.quantidade:
                disponivel = estoque.quantidade_disponivel if estoque else 0
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail={
                        "error": "ESTOQUE_INSUFICIENTE",
                        "message": "Não há quantidade suficiente para atender ao item solicitado.",
                        "details": [{"field": f"produtoId {item_in.produtoId}", "issue": f"Disponível: {disponivel}, Solicitado: {item_in.quantidade}"}]
                    }
                )

            subtotal = round(produto.preco * item_in.quantidade, 2)
            valor_total += subtotal
            itens_a_inserir.append((produto.id, item_in.quantidade, produto.preco, subtotal))

        pedido_db = PedidoDB(
            cliente_id=usuario_id,
            unidade_id=dados.unidadeId,
            canal_pedido=dados.canalPedido.value,
            status="AGUARDANDO_PAGAMENTO",
            valor_total=round(valor_total, 2)
        )
        db.add(pedido_db)
        db.flush()

        for prod_id, qtd, pr_unit, sub in itens_a_inserir:
            db.add(ItemPedidoDB(
                pedido_id=pedido_db.id,
                produto_id=prod_id,
                quantidade=qtd,
                preco_unitario=pr_unit,
                subtotal=sub
            ))

        db.commit()
        db.refresh(pedido_db)
        return pedido_db

class PaymentMockService:
    @staticmethod
    def processar_mock(db: Session, dados: PagamentoMockRequest, usuario_id: int):
        pedido = db.query(PedidoDB).filter(PedidoDB.id == dados.pedidoId).first()
        if not pedido:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "PEDIDO_NAO_ENCONTRADO", "message": f"Pedido {dados.pedidoId} inexistente."}
            )

        if pedido.status != "AGUARDANDO_PAGAMENTO":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"error": "STATUS_INVALIDO", "message": f"Pedido encontra-se em status '{pedido.status}', não aguarda pagamento."}
            )

        tx_id = f"mock-tx-{uuid.uuid4().hex[:10]}"

        if dados.simularAprovacao:
            for item in pedido.itens:
                estoque = db.query(EstoqueDB).filter(
                    EstoqueDB.unidade_id == pedido.unidade_id,
                    EstoqueDB.produto_id == item.produto_id
                ).first()
                if estoque:
                    estoque.quantidade_disponivel -= item.quantidade
                    estoque.atualizado_em = datetime.now(timezone.utc)

            pedido.status = "EM_PREPARO"
            pagamento = PagamentoDB(
                pedido_id=pedido.id,
                transacao_id=tx_id,
                metodo=dados.metodo.value,
                status="APROVADO",
                payload_retorno=json.dumps({"tx": tx_id, "status": "APPROVED", "valor": pedido.valor_total})
            )
            db.add(pagamento)

            db.add(AuditoriaLogDB(
                usuario_id=usuario_id,
                acao="PAGAMENTO_APROVADO_MOCK",
                entidade="PEDIDO",
                registro_id=pedido.id,
                detalhes_json=json.dumps({"statusAnterior": "AGUARDANDO_PAGAMENTO", "novoStatus": "EM_PREPARO", "tx": tx_id})
            ))
            db.commit()

            return {
                "transacaoId": tx_id,
                "pedidoId": pedido.id,
                "statusPagamento": "APROVADO",
                "novoStatusPedido": "EM_PREPARO",
                "mensagem": "Pagamento confirmado com sucesso via mock gateway."
            }
        else:
            pagamento = PagamentoDB(
                pedido_id=pedido.id,
                transacao_id=tx_id,
                metodo=dados.metodo.value,
                status="RECUSADO",
                payload_retorno=json.dumps({"tx": tx_id, "status": "DECLINED", "reason": "Saldo insuficiente no emissor"})
            )
            db.add(pagamento)
            db.add(AuditoriaLogDB(
                usuario_id=usuario_id,
                acao="PAGAMENTO_RECUSADO_MOCK",
                entidade="PEDIDO",
                registro_id=pedido.id,
                detalhes_json=json.dumps({"motivo": "Simulação de recusa financeira"})
            ))
            db.commit()

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": "PAGAMENTO_RECUSADO",
                    "message": "A operadora simulada recusou a transação financeira.",
                    "details": [{"field": "pagamento", "issue": "Transação rejeitada pelo mock gateway"}]
                }
            )
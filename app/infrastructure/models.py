from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import Integer, String, Boolean, Float, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.infrastructure.database import Base

class UsuarioDB(Base):
    __tablename__ = "usuarios"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(120), unique=True, index=True, nullable=False)
    senha_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    perfil: Mapped[str] = mapped_column(String(20), nullable=False)
    consentimento_fidelidade: Mapped[bool] = mapped_column(Boolean, nullable=True, default=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime, nullable=True, default=lambda: datetime.now(timezone.utc))

class UnidadeDB(Base):
    __tablename__ = "unidades"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    cnpj: Mapped[str] = mapped_column(String(18), unique=True, nullable=False)
    cidade: Mapped[str] = mapped_column(String(80), nullable=False)
    estado: Mapped[str] = mapped_column(String(2), nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=True, default=True)

class ProdutoDB(Base):
    __tablename__ = "produtos"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    nome: Mapped[str] = mapped_column(String(100), nullable=False)
    descricao: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    preco: Mapped[float] = mapped_column(Float, nullable=False)
    categoria: Mapped[str] = mapped_column(String(50), nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=True, default=True)

class EstoqueDB(Base):
    __tablename__ = "estoques"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    unidade_id: Mapped[int] = mapped_column(Integer, ForeignKey("unidades.id"), nullable=False)
    produto_id: Mapped[int] = mapped_column(Integer, ForeignKey("produtos.id"), nullable=False)
    quantidade_disponivel: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    atualizado_em: Mapped[datetime] = mapped_column(DateTime, nullable=True, default=lambda: datetime.now(timezone.utc))
    __table_args__ = (UniqueConstraint('unidade_id', 'produto_id', name='_unidade_produto_uc'),)

    produto: Mapped["ProdutoDB"] = relationship("ProdutoDB")
    unidade: Mapped["UnidadeDB"] = relationship("UnidadeDB")

class PedidoDB(Base):
    __tablename__ = "pedidos"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    cliente_id: Mapped[int] = mapped_column(Integer, ForeignKey("usuarios.id"), nullable=False)
    unidade_id: Mapped[int] = mapped_column(Integer, ForeignKey("unidades.id"), nullable=False)
    canal_pedido: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="AGUARDANDO_PAGAMENTO", nullable=False)
    valor_total: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime, nullable=True, default=lambda: datetime.now(timezone.utc))

    itens: Mapped[list["ItemPedidoDB"]] = relationship("ItemPedidoDB", back_populates="pedido")
    pagamento: Mapped[Optional["PagamentoDB"]] = relationship("PagamentoDB", uselist=False, back_populates="pedido")

class ItemPedidoDB(Base):
    __tablename__ = "itens_pedido"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    pedido_id: Mapped[int] = mapped_column(Integer, ForeignKey("pedidos.id"), nullable=False)
    produto_id: Mapped[int] = mapped_column(Integer, ForeignKey("produtos.id"), nullable=False)
    quantidade: Mapped[int] = mapped_column(Integer, nullable=False)
    preco_unitario: Mapped[float] = mapped_column(Float, nullable=False)
    subtotal: Mapped[float] = mapped_column(Float, nullable=False)

    pedido: Mapped["PedidoDB"] = relationship("PedidoDB", back_populates="itens")
    produto: Mapped["ProdutoDB"] = relationship("ProdutoDB")

class PagamentoDB(Base):
    __tablename__ = "pagamentos"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    pedido_id: Mapped[int] = mapped_column(Integer, ForeignKey("pedidos.id"), nullable=False)
    transacao_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    metodo: Mapped[str] = mapped_column(String(30), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    payload_retorno: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime, nullable=True, default=lambda: datetime.now(timezone.utc))

    pedido: Mapped["PedidoDB"] = relationship("PedidoDB", back_populates="pagamento")

class AuditoriaLogDB(Base):
    __tablename__ = "auditoria_logs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    usuario_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    acao: Mapped[str] = mapped_column(String(100), nullable=False)
    entidade: Mapped[str] = mapped_column(String(50), nullable=False)
    registro_id: Mapped[int] = mapped_column(Integer, nullable=False)
    detalhes_json: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime, nullable=True, default=lambda: datetime.now(timezone.utc))
from datetime import datetime, timezone
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.exceptions import RequestValidationError
from app.infrastructure.database import engine, Base, SessionLocal
from app.infrastructure.models import UsuarioDB, UnidadeDB, ProdutoDB, EstoqueDB
from app.core.security import hash_senha
from app.core.config import PROJECT_NAME
from app.api.routers import auth, produtos, pedidos, pagamentos, admin

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=PROJECT_NAME,
    description="API RESTful para a rede de franquias Raízes do Nordeste com suporte a multicanalidade, estoque por loja e pagamento mock desacoplado.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        field = " -> ".join([str(loc) for loc in err.get("loc", [])])
        errors.append({"field": field, "issue": err.get("msg")})
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "VALIDACAO_FALHOU",
            "message": "A requisição possui campos inválidos ou ausentes.",
            "details": errors,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "path": request.url.path
        }
    )

app.include_router(auth.router, prefix="/api/v1")
app.include_router(produtos.router, prefix="/api/v1")
app.include_router(pedidos.router, prefix="/api/v1")
app.include_router(pagamentos.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")

@app.get("/", include_in_schema=False)
def raiz():
    return RedirectResponse(url="/docs")

@app.on_event("startup")
def seed_dados():
    db = SessionLocal()
    try:
        if db.query(UsuarioDB).count() == 0:
            db.add_all([
                UsuarioDB(nome="Dona Francisca", email="cliente@raizes.com", senha_hash=hash_senha("SenhaValida123"), perfil="CLIENTE", consentimento_fidelidade=True),
                UsuarioDB(nome="Atendente Balcão", email="atendente@raizes.com", senha_hash=hash_senha("SenhaValida123"), perfil="ATENDENTE"),
                UsuarioDB(nome="Gerente Geral", email="gerente@raizes.com", senha_hash=hash_senha("SenhaValida123"), perfil="GERENTE")
            ])
            db.commit()

        if db.query(UnidadeDB).count() == 0:
            u1 = UnidadeDB(nome="Unidade 1 - Recife Boa Viagem", cnpj="12.345.678/0001-90", cidade="Recife", estado="PE", ativo=True)
            db.add(u1)
            db.commit()
            db.refresh(u1)

            p1 = ProdutoDB(nome="Cuscuz com Carne de Sol e Queijo", descricao="Cuscuz nordestino recheado no vapor", preco=18.00, categoria="Cuscuz", ativo=True)
            p2 = ProdutoDB(nome="Tapioca Rendada", descricao="Tapioca crocante com queijo coalho e manteiga de garrafa", preco=15.00, categoria="Tapiocas", ativo=True)
            p3 = ProdutoDB(nome="Bolo de Macaxeira Tradicional", descricao="Fatia artesanal de bolo de macaxeira", preco=12.50, categoria="Bolos", ativo=True)
            db.add_all([p1, p2, p3])
            db.commit()
            db.refresh(p1); db.refresh(p2); db.refresh(p3)

            db.add_all([
                EstoqueDB(unidade_id=u1.id, produto_id=p1.id, quantidade_disponivel=10),
                EstoqueDB(unidade_id=u1.id, produto_id=p2.id, quantidade_disponivel=15),
                EstoqueDB(unidade_id=u1.id, produto_id=p3.id, quantidade_disponivel=5)
            ])
            db.commit()
    finally:
        db.close()
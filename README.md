# Rede "Raízes do Nordeste" - API Back-End

API RESTful desenvolvida para a disciplina de **Projeto Multidisciplinar (Trilha Back-End)** da UNINTER.

## 🚀 Tecnologias Utilizadas
- **Python 3.13**
- **FastAPI** (Framework web assíncrono e OpenAPI)
- **SQLAlchemy** (ORM de persistência)
- **SQLite** (Banco de dados relacional embarcado)
- **Pydantic v2** (Validação e contratos tipados)
- **PyJWT & BCrypt** (Segurança, hash e Bearer Tokens)

## 📌 Arquitetura em Camadas
O projeto adota Clean Architecture com separação rigorosa de responsabilidades:
- `app/api`: Rotas, controladores HTTP e schemas Pydantic de entrada/saída.
- `app/application`: Serviços de orquestração de casos de uso (Auth, Pedidos e Pagamentos).
- `app/domain`: Entidades e enums de regras de negócio essenciais (`canalPedido`, `status`).
- `app/infrastructure`: Modelos ORM e configuração da base relacional.
- `app/core`: Segurança, hashing BCrypt e geração de tokens JWT.

---

## ⚙️ Instruções de Execução Local

### 1. Clonar o Repositório
```bash
git clone <URL_DO_SEU_REPOSITORIO>
cd raizes-do-nordeste-api
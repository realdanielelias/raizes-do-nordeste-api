# Rede "Raízes do Nordeste" — API Back-End

API RESTful desenvolvida como requisito avaliativo da disciplina Projeto Multidisciplinar — Trilha Back-End do Centro Universitário Internacional UNINTER.

Aluno: Daniel Elias de Souza
RU: 4590111
Polo: Marília
Ano / Semestre: 2026
Docente Responsável: Profa. Me. Luciane Yanase Kanashiro
Repositório Público: https://github.com/realdanielelias/raizes-do-nordeste-api

---

## 1. Visão Geral do Sistema

A solução centraliza as operações mercantis e de faturamento da rede de franquias de alimentação regional "Raízes do Nordeste", implementando:
1. Multicanalidade Obrigatória (canalPedido): Suporte nativo e rastreabilidade para os canais APP, TOTEM, BALCAO, PICKUP e WEB.
2. Segregação de Inventário por Unidade: Controle atômico de saldos físicos de estoque isolados por filial.
3. Desacoplamento Financeiro (Mock Gateway): Processamento síncrono simulado de pagamentos sem retenção de dados sensíveis de cartão no núcleo transacional.
4. Segurança e LGPD: Criptografia irreversível de senhas (BCrypt custo 12), autenticação stateless com Bearer Token JWT e trilha de auditoria para operações críticas.

---

## 2. Tecnologias e Requisitos do Ambiente

- Linguagem: Python 3.13 (compatível com 3.10+)
- Framework Web: FastAPI (ASGI / OpenAPI 3.0)
- Servidor ASGI: Uvicorn
- ORM e Persistência: SQLAlchemy 2.0+ com SQLite (base relacional embarcada)
- Validação de Dados: Pydantic v2 & email-validator
- Segurança e Criptografia: PyJWT (HMAC-SHA256) e BCrypt
- Testes e Contratos: Postman Collection v2.1

---

## 3. Arquitetura em Camadas (Separation of Concerns)

O projeto adota os preceitos da Clean Architecture, segregando responsabilidades em 4 camadas concêntricas:

'''text
raizes-do-nordeste-api/
├── app/
│   ├── __init__.py
│   ├── core/                      # Configurações globais, variáveis e segurança JWT/BCrypt
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── security.py
│   ├── domain/                    # Entidades corporativas e enumerações tipadas do negócio
│   │   ├── __init__.py
│   │   └── enums.py
│   ├── infrastructure/            # Modelos ORM, conexão relacional e adaptadores
│   │   ├── __init__.py
│   │   ├── database.py
│   │   └── models.py
│   ├── application/               # Orquestração dos casos de uso e serviços de aplicação
│   │   ├── __init__.py
│   │   └── services.py
│   └── api/                       # Controladores de rota, contratos de entrada/saída (DTOs)
│       ├── __init__.py
│       ├── schemas.py
│       └── routers/
│           ├── __init__.py
│           ├── auth.py            # Autenticação e login
│           ├── produtos.py        # Cardápio e catálogo local
│           ├── pedidos.py         # Fluxo crítico de pedidos e status
│           ├── pagamentos.py      # Integração de pagamento mock
│           └── admin.py           # Gestão restrita de estoque (RBAC)
├── .env.example                   # Modelo das variáveis de configuração
├── .gitignore                     # Arquivos ignorados pelo controle de versão
├── requirements.txt               # Relação determinística de dependências
├── README.md                      # Documentação técnica e guia de execução
├── postman_collection.json        # Coleção com os 10 cenários de testes
└── main.py                        # Ponto de entrada da aplicação e rotina de seed

'''
---

## 4. Guia de Execução Local (Passo a Passo)

### 4.1 Clonar o Repositório
git clone https://github.com/realdanielelias/raizes-do-nordeste-api.git
cd raizes-do-nordeste-api

### 4.2 Configurar o Ambiente Virtual
Linux / macOS:
python3 -m venv venv
source venv/bin/activate

Windows:
python -m venv venv
venv\Scripts\activate

### 4.3 Instalar as Dependências
pip install -r requirements.txt

### 4.4 Configurar as Variáveis de Ambiente
cp .env.example .env

### 4.5 Banco de Dados, Migrations e Carga Inicial (Seed)
A aplicação conta com geração e migração relacional automática. Na inicialização do servidor, o script main.py executa Base.metadata.create_all() e povoa o banco com dados de teste (seed):
- 3 Usuários com perfis RBAC: CLIENTE, ATENDENTE e GERENTE.
- 1 Franquia operacional: Unidade 1 - Recife Boa Viagem.
- 3 Produtos regionais com estoque ativo: Cuscuz Recheado, Tapioca Rendada e Bolo de Macaxeira.

### 4.6 Iniciar o Servidor da API
uvicorn main:app --reload --port 8000

A API estará em execução no endereço: http://localhost:8000

---

## 5. Documentação Interativa da API (OpenAPI / Swagger)

Com a aplicação em execução, acesse no navegador:
- Swagger UI: http://localhost:8000/docs
- Especificação OpenAPI (JSON): http://localhost:8000/openapi.json

---

## 6. Plano de Testes e Evidências (Postman)

A suíte de testes está formalizada no arquivo postman_collection.json na raiz do repositório. Ela cobre 10 cenários determinísticos (6 positivos e 4 negativos):

- T01 | Positivo | Login com credenciais válidas e emissão de JWT (POST /api/v1/auth/login) -> HTTP 200 OK
- T02 | Positivo | Consulta de cardápio por filial ativa (GET /api/v1/produtos?unidadeId=1) -> HTTP 200 OK
- T03 | Positivo | Criação de pedido via TOTEM com estoque regular (POST /api/v1/pedidos) -> HTTP 201 Created
- T04 | Positivo | Criação de pedido via APP mobile (POST /api/v1/pedidos) -> HTTP 201 Created
- T05 | Positivo | Liquidação com Gateway Mock (Aprovação) -> EM_PREPARO (POST /api/v1/pagamentos/mock) -> HTTP 200 OK
- T06 | Positivo | Atualização de status pela cozinha -> PRONTO (PATCH /api/v1/pedidos/1/status) -> HTTP 200 OK
- T07 | Negativo | Tentativa de acesso sem Token JWT (GET /api/v1/pedidos) -> HTTP 401 Unauthorized
- T08 | Negativo | Perfil CLIENTE tentando acessar ajuste de GERENTE (POST /api/v1/unidades/estoque/ajuste) -> HTTP 403 Forbidden
- T09 | Negativo | Criação de pedido com canalPedido inválido (POST /api/v1/pedidos) -> HTTP 422 Unprocessable Entity
- T10 | Negativo | Pedido com quantidade superior ao estoque físico (POST /api/v1/pedidos) -> HTTP 409 Conflict

### Como Executar os Testes no Postman:
1. Abra o Postman e clique em Import.
2. Selecione o arquivo postman_collection.json da raiz deste projeto.
3. Execute o teste T01 (Login) primeiro para obter o accessToken.
4. Copie o token e atualize a variável tokenCliente da coleção.
5. Execute os testes na ordem numérica sugerida (T01 a T10).

---

## 7. Credenciais Pré-Cadastradas no Seed:
- Cliente: cliente@raizes.com | Senha: SenhaValida123 (Perfil: CLIENTE)
- Atendente: atendente@raizes.com | Senha: SenhaValida123 (Perfil: ATENDENTE)
- Gerente: gerente@raizes.com | Senha: SenhaValida123 (Perfil: GERENTE)
# SIGESCON - Sistema de Gestão de Contratos

SIGESCON é uma API back-end robusta, desenvolvida em Python com o framework Flask, projetada para gerenciar o ciclo de vida completo de contratos, seus relatórios fiscais e os usuários associados. A aplicação implementa um fluxo de trabalho claro para a criação de pendências, submissão e aprovação de relatórios, com um sistema de permissões baseado em perfis de usuário.

---

## **Principais Funcionalidades**

* **Autenticação Segura**: Sistema de login baseado em JSON Web Tokens (JWT) para proteger os endpoints da API.
* **Gerenciamento de Usuários com Perfis**: Controle de acesso granular com três perfis distintos:
    * **Administrador**: Acesso total ao sistema.
    * **Gestor**: Permissões de visualização para os contratos que gerencia.
    * **Fiscal**: Permissões para visualizar seus contratos e gerenciar o fluxo de relatórios fiscais.
* **CRUD Completo**: Operações de Criar, Ler, Atualizar e Deletar para os principais recursos do sistema:
    * Contratos
    * Contratados (Empresas/Pessoas)
    * Usuários
* **Ciclo de Vida de Relatórios Fiscais**:
    * Administradores podem criar **pendências** para os fiscais (ex: "Enviar relatório mensal").
    * Fiscais podem **submeter relatórios** (com upload de arquivos) para atender a essas pendências.
    * Administradores podem **aprovar** ou **rejeitar** os relatórios enviados, fornecendo feedback.
    * Fiscais podem **reenviar** versões corrigidas de relatórios rejeitados.
* **Upload de Arquivos**: Suporte para anexar documentos importantes, como o arquivo principal do contrato e os relatórios fiscais.
* **Soft Delete**: Os registros não são permanentemente excluídos do banco de dados, mas sim marcados como inativos, preservando a integridade e o histórico dos dados.
* **Testes de Integração**: Acompanha um script de teste (`test_realistic_workflow.py`) que simula um fluxo de trabalho completo, garantindo a estabilidade da aplicação.

---

## **Tecnologias Utilizadas**

* **Back-end**: Python 3, Flask
* **Banco de Dados**: PostgreSQL
* **Autenticação**: Flask-JWT-Extended
* **Conector DB**: psycopg2-binary
* **Variáveis de Ambiente**: python-dotenv

---

## **Pré-requisitos**

Antes de começar, certifique-se de que você tem os seguintes softwares instalados em sua máquina:
* Python 3.8+
* pip (gerenciador de pacotes do Python)
* venv (para criar ambientes virtuais)
* PostgreSQL (servidor de banco de dados)

---

## **Guia de Instalação e Configuração**

Siga os passos abaixo para configurar e executar o projeto localmente.

### **1. Clonar o Repositório**

```bash
git clone <url_do_seu_repositorio>
cd py-back-contratos
```

### **2. Configurar o Ambiente Virtual e Instalar as Dependências**

É altamente recomendável usar um ambiente virtual para isolar as dependências do projeto.

```bash
# Criar o ambiente virtual
python -m venv venv

# Ativar o ambiente virtual
# No Windows:
venv\Scripts\activate
# No macOS/Linux:
source venv/bin/activate

# Instalar as bibliotecas necessárias
pip install Flask Flask-Cors Flask-JWT-Extended psycopg2-binary python-dotenv Werkzeug
```

### **3. Configurar o Banco de Dados**

1.  Acesse seu servidor PostgreSQL.
2.  Crie um novo banco de dados para o projeto. Ex: `CREATE DATABASE contratos;`.
3.  Execute o script `DB/database.sql` para criar todas as tabelas e seus relacionamentos. Você pode usar uma ferramenta como DBeaver, pgAdmin ou o próprio `psql`.

### **4. Configurar as Variáveis de Ambiente**

1.  Na raiz do projeto, crie um arquivo chamado **`.env`**.
2.  Copie o conteúdo abaixo para o seu arquivo `.env` e **substitua os valores** pelos da sua configuração local.

    ```ini
    # Configuração do Banco de Dados PostgreSQL
    DB_USER=seu_usuario_postgres
    DB_PASSWORD=sua_senha_segura
    DB_HOST=localhost
    DB_PORT=5432
    DB_NAME=contratos 

    # Chave secreta para JWT - ESSENCIAL PARA SEGURANÇA
    # Use uma string aleatória e longa. Não compartilhe esta chave.
    JWT_SECRET_KEY=uma_chave_secreta_muito_longa_e_dificil_de_adivinhar

    # Credenciais para o usuário Administrador que será criado
    ADMIN_EMAIL=admin@exemplo.com
    ADMIN_PASSWORD=senha_forte_admin
    ```

### **5. Popular o Banco com Dados Iniciais (Seeding)**

A aplicação inclui um comando para popular as tabelas auxiliares (status, perfis, etc.) e criar o primeiro usuário Administrador com base nas credenciais do seu arquivo `.env`.

Execute o seguinte comando no terminal (com o ambiente virtual ativado):

```bash
flask seed-db
```

Após a execução, a mensagem `"Seed do banco de dados concluído com sucesso!"` deve aparecer.

---

## **Executando a Aplicação**

Com o ambiente virtual ativado e as configurações prontas, inicie o servidor de desenvolvimento Flask:

```bash
flask run
```

A API estará disponível em `http://127.0.0.1:5000`.

---

## **Executando os Testes**

Para verificar a integridade e o funcionamento dos principais fluxos da API, execute o script de teste. Certifique-se de que a aplicação esteja rodando em um terminal e execute o seguinte comando em **outro terminal**:

```bash
python test_realistic_workflow.py
```

O script irá simular um fluxo completo: login, criação de usuários, contratos, envio e análise de relatórios, e por fim, a limpeza dos dados criados.

---

## **Estrutura do Projeto**

```
.
├── app/
│   ├── repository/  # Camada de acesso aos dados (interação com o banco)
│   ├── routes/      # Definição dos endpoints (rotas) da API
│   ├── __init__.py  # Fábrica da aplicação Flask e registro de blueprints
│   ├── auth_decorators.py # Decorators de permissão (@admin_required)
│   ├── db.py        # Configuração da conexão com o banco de dados
│   └── seeder.py    # Lógica para popular o banco de dados inicial
├── DB/
│   ├── database.sql # Script de criação de todas as tabelas
│   └── inserts.sql  # Exemplos de inserções manuais
├── uploads/         # Pasta onde os arquivos enviados são armazenados
├── .env             # Arquivo (local) com as variáveis de ambiente
├── .gitignore       # Arquivos e pastas ignorados pelo Git
├── run.py           # Ponto de entrada para executar a aplicação
└── test_realistic_workflow.py # Script de teste de integração
```
# 🔍 LogWatcher

> Ferramenta em Python para monitoramento de tabelas de log/auditoria e do arquivo de log (LDF) do SQL Server, com operações de manutenção seguras.

![Python](https://img.shields.io/badge/Python-3.13%2B-blue?logo=python&logoColor=white)
![SQL Server](https://img.shields.io/badge/SQL%20Server-Compatible-CC2927?logo=microsoftsqlserver&logoColor=white)
![Status](https://img.shields.io/badge/status-em%20desenvolvimento-yellow)
![License](https://img.shields.io/badge/license-MIT-green)

---

## 📌 Sobre o projeto

O **LogWatcher** nasceu para facilitar o dia a dia de analistas de suporte e administradores de banco de dados, centralizando em uma única ferramenta:

- 📊 Consumo de tabelas de log e auditoria
- 💾 Tamanho e utilização do arquivo de log (LDF)
- 🧹 Operações de manutenção (`TRUNCATE`, `DELETE`, `DBCC SHRINKFILE`)

Hoje a ferramenta é usada por uma interface de terminal (**CLI**). A próxima etapa é uma interface gráfica em **CustomTkinter**, reaproveitando toda a lógica de negócio já implementada — as duas interfaces vão conviver sobre o mesmo código de domínio.

> ⚠️ **Atenção:** o LogWatcher executa comandos destrutivos e irreversíveis no banco. Use sempre com um usuário de permissões controladas e valide o ambiente (produção x homologação) antes de confirmar qualquer operação.

---

## ✨ Funcionalidades

| Categoria | Recurso |
| --- | --- |
| **Conexão** | Conexão com SQL Server via perfis salvos em JSON |
| **Monitoramento** | Consulta das tabelas definidas em cada perfil |
| **Dashboard** | Tabelas monitoradas, quantidade de linhas e espaço reservado/utilizado |
| **Status do log** | `Recovery Model` e `Log Reuse Wait` |
| **Manutenção** | `TRUNCATE TABLE`, `DELETE` e `DBCC SHRINKFILE` (automático) |
| **Segurança** | Confirmação obrigatória antes de operações destrutivas |

---

## 🏗️ Arquitetura

O projeto segue uma organização em camadas, favorecendo a separação de responsabilidades e a manutenção:

```text
logwatcher/
├── app/
│   ├── config/         # Configurações de conexão
│   ├── models/         # Entidades de domínio (LogTable, LogFile, ConnectionProfile...)
│   ├── repositories/   # Acesso ao SQL Server
│   ├── services/       # Regras de negócio
│   └── views/
│       └── cli/        # Interface via terminal
├── data/
│   └── connections.json
├── tests/
│   ├── test_logwatcher_cli.py
│   └── test_profiles.py
├── requirements.txt
└── README.md
```

| Camada | Responsabilidade |
| --- | --- |
| **Config** | Parâmetros e configurações de conexão |
| **Models** | Objetos de domínio (`LogTable`, `LogFile`, `ConnectionProfile`...) |
| **Repositories** | Acesso e queries ao SQL Server |
| **Services** | Regras de negócio e orquestração das operações |
| **Views** | Interfaces de uso da aplicação (CLI e, futuramente, GUI) |
| **Tests** | Scripts de validação usados durante o desenvolvimento |

> A pasta `venv/` é local e não deve ser versionada — mantenha-a no `.gitignore`.

---

## 🚀 Como executar

### Pré-requisitos

- [Python 3.13+](https://www.python.org/downloads/)
- SQL Server (local ou remoto)
- Driver ODBC para SQL Server instalado na máquina
- Git (opcional)

### 1. Clonar o repositório

```bash
git clone <url-do-repositorio>
cd logwatcher
```

### 2. Criar o ambiente virtual

**Windows (PowerShell)**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Linux / macOS**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar as dependências

```bash
pip install -r requirements.txt
```

### 4. Executar a CLI

```bash
python -m app.views.cli.logwatcher_cli
```

O arquivo `tests/test_logwatcher_cli.py` é destinado apenas aos testes das funcionalidades da CLI e não serve mais como ponto de entrada da aplicação.

---

## 💾 Perfis de conexão

Os perfis ficam em `data/connections.json`. Cada perfil armazena:

- Nome da conexão
- Servidor
- Banco de dados
- Usuário
- Tabelas monitoradas

> 🔒 **Segurança:** a senha **não** é armazenada. Ela é solicitada a cada nova conexão.

---

## 🛠️ Tecnologias utilizadas

- **Python 3.13** e Programação Orientada a Objetos
- **SQL Server**
- [`tabulate`](https://pypi.org/project/tabulate/) — formatação de tabelas no terminal
- `pathlib` — manipulação de caminhos
- `json` — persistência dos perfis
- `dataclasses` — modelagem dos objetos de domínio
- **CustomTkinter** — interface gráfica prevista para a próxima versão

---

## 📋 Roadmap

### ✅ Concluído (CLI)

- [x] Conexão com SQL Server
- [x] Dashboard via terminal
- [x] Consulta de tabelas monitoradas
- [x] Consulta do arquivo de log
- [x] Status do log
- [x] `TRUNCATE`
- [x] `DELETE`
- [x] `SHRINK` automático
- [x] Perfis salvos em JSON

### 🔜 Próxima versão

- [ ] Interface gráfica com CustomTkinter
- [ ] Dashboard visual
- [ ] Gerenciamento visual de perfis
- [ ] Modais de confirmação
- [ ] Atualização da interface sem reiniciar a aplicação

---

## 📚 Objetivo do projeto

Projeto desenvolvido como estudo prático de:

- Arquitetura em camadas
- Programação Orientada a Objetos em Python
- Integração com SQL Server
- Desenvolvimento de aplicações desktop
- Organização de código e versionamento com Git

---

## 📄 Licença

Distribuído sob a licença MIT. Sinta-se à vontade para usar, estudar e adaptar.
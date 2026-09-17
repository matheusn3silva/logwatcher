# 🔍 LogWatcher

> Ferramenta em Python para monitoramento de tabelas de log/auditoria e arquivos de log (LDF) do SQL Server, com operações de manutenção seguras.

[![Python](https://img.shields.io/badge/Python-3.13%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![SQL Server](https://img.shields.io/badge/SQL%20Server-Compatible-CC2927?logo=microsoftsqlserver&logoColor=white)](https://www.microsoft.com/sql-server)
[![Status](https://img.shields.io/badge/status-em%20desenvolvimento-yellow)]()
[![License](https://img.shields.io/badge/license-MIT-green)]()

---

## 📌 Sobre o projeto

O **LogWatcher** nasceu para facilitar o dia a dia de analistas de suporte e administradores de banco de dados, centralizando em uma única ferramenta:

- 📊 Consumo de tabelas de log e auditoria
- 💾 Tamanho e utilização do arquivo de log (LDF)
- 🧹 Execução de operações de manutenção (`TRUNCATE`, `DELETE`, `DBCC SHRINKFILE`)

Atualmente o projeto conta com uma interface via terminal (**CLI**). A próxima etapa é a migração para uma interface gráfica com **CustomTkinter**, reaproveitando toda a lógica de negócio já implementada.

---

## ✨ Funcionalidades

| Categoria | Recurso |
|---|---|
| **Conexão** | Conexão com SQL Server via perfis salvos em JSON |
| **Monitoramento** | Consulta de tabelas específicas por perfil |
| **Dashboard** | Tabelas monitoradas, quantidade de linhas, espaço reservado/utilizado |
| **Status do log** | `Recovery Model` e `Log Reuse Wait` |
| **Manutenção** | `TRUNCATE TABLE`, `DELETE`, `DBCC SHRINKFILE` (automático) |
| **Segurança** | Confirmação obrigatória antes de operações destrutivas |

---

## 🏗️ Arquitetura

O projeto segue uma organização em camadas, favorecendo separação de responsabilidades e facilidade de manutenção:

```text
logwatcher/
├── app/
│   ├── config/         # Configurações de conexão
│   ├── models/         # Entidades de domínio (LogTable, LogFile, ConnectionProfile...)
│   ├── repositories/   # Acesso ao SQL Server
│   ├── services/       # Regras de negócio da aplicação
│   └── ...
│
├── data/
│   └── connections.json
│
├── tests/
│   ├── test_logwatcher_cli.py
│   └── test_profiles.py
│
├── venv/
├── requirements.txt
└── README.md
```

| Camada | Responsabilidade |
|---|---|
| **Config** | Parâmetros e configurações da conexão |
| **Models** | Objetos de domínio (`LogTable`, `LogFile`, `ConnectionProfile`, etc.) |
| **Repositories** | Acesso e queries ao SQL Server |
| **Services** | Regras de negócio e orquestração das operações |
| **Tests** | Scripts de validação usados durante o desenvolvimento |

---

## 🚀 Como executar

### Pré-requisitos

- [Python 3.13+](https://www.python.org/downloads/)
- SQL Server (local ou remoto)
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

### 3. Instalar as dependências

```bash
pip install -r requirements.txt
```

### 4. Executar a aplicação

```bash
python -m tests.test_logwatcher_cli
```

---

## 💾 Perfis de conexão

Os perfis de conexão são armazenados em:

```text
data/connections.json
```

Cada perfil armazena:

- Nome da conexão
- Servidor
- Banco de dados
- Usuário
- Tabelas monitoradas

> 🔒 **Segurança:** a senha **não** é armazenada. Ela é solicitada sempre que uma nova conexão é aberta.

---

## 🛠️ Tecnologias utilizadas

- **Python 3.13**
- **SQL Server**
- [`tabulate`](https://pypi.org/project/tabulate/) — formatação de tabelas no terminal
- `pathlib` — manipulação de caminhos
- `json` — persistência dos perfis de conexão
- `dataclasses` — modelagem dos objetos de domínio
- Programação Orientada a Objetos (POO)

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

Este projeto foi desenvolvido como estudo prático de:

- Arquitetura em camadas
- Programação Orientada a Objetos em Python
- Integração com SQL Server
- Desenvolvimento de aplicações desktop
- Boas práticas de organização de código e versionamento com Git

---

## 📄 Licença

Este projeto está sob a licença MIT. Sinta-se à vontade para usar, estudar e adaptar.

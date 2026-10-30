# 🔍 LogWatcher

> Ferramenta em Python para monitoramento de tabelas de log/auditoria e do arquivo de log (LDF) do SQL Server, com operações de manutenção seguras.

![Python](https://img.shields.io/badge/Python-3.13%2B-blue?logo=python&logoColor=white)
![SQL Server](https://img.shields.io/badge/SQL%20Server-Compatible-CC2927?logo=microsoftsqlserver&logoColor=white)
![Status](https://img.shields.io/badge/status-em%20desenvolvimento-yellow)
![License](https://img.shields.io/badge/license-MIT-green)
[![Download](https://img.shields.io/github/v/release/matheusn3silva/logwatcher?label=Download&style=flat-square)](https://github.com/matheusn3silva/logwatcher/releases/latest)

---

## 📥 Download

A forma mais simples de usar o LogWatcher no Windows é baixando o instalador já pronto, sem precisar instalar Python ou dependências:

👉 **[Baixar a última versão](https://github.com/mathuesn3silva/logwatcher/releases/latest)**

O instalador (`LogWatcher-Setup-X.X.exe`) cria atalhos para a GUI e para a CLI, e não exige privilégios de administrador por padrão.

---

## 📌 Sobre o projeto

O **LogWatcher** nasceu para facilitar o dia a dia de analistas de suporte e administradores de banco de dados, centralizando em uma única ferramenta:

- 📊 Consumo de tabelas de log e auditoria
- 💾 Tamanho e utilização do arquivo de log (LDF)
- 🧹 Operações de manutenção (`TRUNCATE`, `DELETE`, `DBCC SHRINKFILE`)
- 🧾 Log de auditoria de todas as operações executadas

A ferramenta hoje conta com **duas interfaces completas e independentes**, que compartilham toda a lógica de negócio:

- **CLI** — interface de terminal colorida, com navegação por setas (via `questionary`)
- **GUI** — interface gráfica em **CustomTkinter**, com tema inspirado no **Dracula**

> ⚠️ **Atenção:** o LogWatcher executa comandos destrutivos e irreversíveis no banco. Use sempre com um usuário de permissões controladas e valide o ambiente (produção x homologação) antes de confirmar qualquer operação.

---

## ✨ Funcionalidades

| Categoria | Recurso |
| --- | --- |
| **Conexão** | Conexão com SQL Server via perfis salvos em JSON (driver `mssql_python`) |
| **Monitoramento** | Consulta das tabelas definidas em cada perfil |
| **Dashboard** | Tabelas monitoradas, quantidade de linhas e espaço reservado/utilizado |
| **Status do log** | `Recovery Model` e `Log Reuse Wait` |
| **Manutenção** | `TRUNCATE TABLE`, `DELETE` e `DBCC SHRINKFILE` (automático) |
| **Segurança** | Confirmação obrigatória antes de operações destrutivas |
| **Auditoria** | Registro em arquivo de log diário: usuário SQL, usuário do Windows, perfil, ação e status de cada operação |
| **CLI** | Menus navegáveis por setas e saída colorida |
| **GUI** | Interface gráfica completa (dashboard, perfis, logs e manutenção) com tema Dracula |
| **Distribuição** | Build de executáveis Windows (GUI + CLI) via PyInstaller e instalador via Inno Setup |

---

## 🏗️ Arquitetura

O projeto segue uma organização em camadas, favorecendo a separação de responsabilidades e a manutenção. A lógica de domínio é 100% compartilhada entre CLI e GUI — apenas a camada `views` muda, chamando os `services` diretamente:

```text
logwatcher/
├── app/
│   ├── config/          # Configurações de conexão
│   ├── controllers/     # Reservado para orquestração entre views e services (ainda não implementado)
│   ├── models/          # Entidades de domínio (ConnectionProfile, LogTable,
│   │                     LogFile, DataFile, DatabaseStatus, DashboardSummary,
│   │                     ShrinkResult...)
│   ├── repositories/    # Acesso ao SQL Server
│   ├── services/        # Regras de negócio (conexão, perfis, logwatcher, parser)
│   ├── utils/           # Utilitários (ex.: log de auditoria)
│   └── views/
│       ├── cli/          # Interface via terminal (colorida, navegação por setas)
│       └── gui/           # Interface gráfica (CustomTkinter)
│           ├── dashboard_views/
│           ├── log_views/
│           ├── maintenance_views/
│           └── profile_views/
├── assets/               # Ícones e logo do app (.ico, .png, .svg)
├── data/
│   └── connections.json  # Perfis de conexão salvos
├── logs/
│   └── logwatcher_audit_AAAA-MM-DD.log  # Log de auditoria diário
├── main.py               # Entrypoint da GUI
├── main_cli.py            # Entrypoint da CLI
├── logwatcher.spec        # Build dos executáveis (PyInstaller)
├── installer.iss          # Instalador Windows (Inno Setup)
├── requirements.txt
└── README.md
```

| Camada | Responsabilidade |
| --- | --- |
| **Config** | Parâmetros e configurações de conexão |
| **Controllers** | Camada reservada para orquestração entre views e services; hoje as views chamam os services diretamente |
| **Models** | Objetos de domínio |
| **Repositories** | Acesso e queries ao SQL Server |
| **Services** | Regras de negócio e orquestração das operações |
| **Utils** | Funções de apoio (ex.: `AuditLogger`) |
| **Views** | Interfaces de uso da aplicação (CLI e GUI) |

> A pasta `venv/` é local e não deve ser versionada — mantenha-a no `.gitignore`.

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

**Linux / macOS**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar as dependências

```bash
pip install -r requirements.txt
```

### 4. Executar

**GUI (interface gráfica):**

```bash
python main.py
```

**CLI (terminal):**

```bash
python main_cli.py
```

---

## 💾 Perfis de conexão

Os perfis ficam em `data/connections.json`. Cada perfil armazena:

- Nome da conexão
- Servidor
- Banco de dados
- Usuário
- Tabelas monitoradas

> 🔒 **Segurança:** a senha **não** é armazenada. Ela é solicitada a cada nova conexão.

## 🧾 Log de auditoria

Toda operação relevante (especialmente as destrutivas) é registrada em `logs/logwatcher_audit_AAAA-MM-DD.log`, com timestamp, status, perfil utilizado, banco, usuário SQL, usuário do Windows e detalhe da ação — garantindo rastreabilidade de quem fez o quê.

---

## 📦 Build e distribuição (Windows)

O projeto já inclui a configuração para gerar executáveis standalone e um instalador Windows:

1. **Gerar os executáveis (GUI + CLI)** com [PyInstaller](https://pyinstaller.org/), usando o spec já configurado (`logwatcher.spec`), que empacota o driver `mssql_python`, o CustomTkinter e os assets:

   ```powershell
   pyinstaller logwatcher.spec
   ```

   Isso gera `LogWatcher.exe` (GUI, sem console) e `LogWatcherCLI.exe` (CLI, com console) em `dist/LogWatcher/`.

2. **Gerar o instalador** com [Inno Setup](https://jrsoftware.org/isinfo.php), usando `installer.iss`: cria atalhos para GUI e CLI, não exige privilégios de administrador por padrão (instala em `%LOCALAPPDATA%\Programs`) e libera escrita em `logs/` e `data/` quando instalado em modo administrador.

---

## 🛠️ Tecnologias utilizadas

- **Python 3.13** e Programação Orientada a Objetos
- **SQL Server**
- [`mssql_python`](https://pypi.org/project/mssql-python/) — driver de conexão com o SQL Server
- [`customtkinter`](https://pypi.org/project/customtkinter/) — interface gráfica
- [`questionary`](https://pypi.org/project/questionary/) — menus interativos e coloridos na CLI
- [`tabulate`](https://pypi.org/project/tabulate/) — formatação de tabelas no terminal
- [`pyinstaller`](https://pyinstaller.org/) — empacotamento dos executáveis
- `pathlib` — manipulação de caminhos
- `json` — persistência dos perfis
- `dataclasses` — modelagem dos objetos de domínio

---

## 📋 Roadmap

### ✅ Concluído

- [x] Conexão com SQL Server
- [x] Dashboard (CLI e GUI)
- [x] Consulta de tabelas monitoradas
- [x] Consulta do arquivo de log
- [x] Status do log
- [x] `TRUNCATE`
- [x] `DELETE`
- [x] `SHRINK` automático
- [x] Perfis salvos em JSON
- [x] Log de auditoria das operações
- [x] Interface gráfica com CustomTkinter (tema Dracula)
- [x] CLI colorida com navegação por setas
- [x] Logo e ícone do app
- [x] Build dos executáveis via PyInstaller
- [x] Instalador Windows via Inno Setup

### 🔜 Próxima versão

- [ ] Refino visual dos diálogos de sucesso/erro da GUI (com scroll para muitas tabelas)
- [ ] Camada de controllers entre views e services
- [ ] Testes automatizados cobrindo services e repositories

---

## 📚 Objetivo do projeto

Projeto desenvolvido como estudo prático de:

- Arquitetura em camadas
- Programação Orientada a Objetos em Python
- Integração com SQL Server
- Desenvolvimento de aplicações desktop (CLI e GUI)
- Organização de código e versionamento com Git
- Empacotamento e distribuição de aplicações Python

---

## 📄 Licença

Distribuído sob a licença MIT. Sinta-se à vontade para usar, estudar e adaptar.

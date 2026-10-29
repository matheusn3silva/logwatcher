# -*- mode: python ; coding: utf-8 -*-

import customtkinter
import os
import mssql_python
import mssql_python_odbc

from PyInstaller.utils.hooks import collect_all

ctk_path = os.path.dirname(customtkinter.__file__)
mssql_path = os.path.dirname(mssql_python.__file__)

mssql_datas, mssql_binaries, mssql_hiddenimports = collect_all("mssql_python")
odbc_datas, odbc_binaries, odbc_hiddenimports = collect_all("mssql_python_odbc")

datas = [
    (ctk_path, "customtkinter"),
    ("assets", "assets"),
    *mssql_datas,
    *odbc_datas,
]

binaries = [
    *mssql_binaries,
    *odbc_binaries,

    (
        os.path.join(mssql_path, "ddbc_bindings.cp313-amd64.pyd"),
        "mssql_python"
    ),

    (
        os.path.join(mssql_path, "msvcp140.dll"),
        "mssql_python"
    ),
]

hiddenimports = [
    "pyodbc",
    "mssql_python",
    "mssql_python.ddbc_bindings",
    "mssql_python_odbc",
    *mssql_hiddenimports,
    *odbc_hiddenimports,
]


gui = Analysis(
    ["main.py"],
    pathex=["."],
    datas=datas,
    binaries=binaries,
    hiddenimports=hiddenimports,
    noarchive=False
)

gui_pyz = PYZ(gui.pure)

gui_exe = EXE(
    gui_pyz,
    gui.scripts,
    [],
    exclude_binaries=True,
    name="LogWatcher",
    console=False,
    icon="assets/logo.ico"
)


cli = Analysis(
    ["main_cli.py"],
    pathex=["."],
    datas=datas,
    binaries=binaries,
    hiddenimports=hiddenimports,
    noarchive=False
)

cli_pyz = PYZ(cli.pure)

cli_exe = EXE(
    cli_pyz,
    cli.scripts,
    [],
    exclude_binaries=True,
    name="LogWatcherCLI",
    console=True,
    icon="assets/logo.ico"
)


coll = COLLECT(
    gui_exe,
    gui.binaries,
    gui.datas,
    cli_exe,
    cli.binaries,
    cli.datas,
    strip=False,
    upx=False,
    name="LogWatcher"
)
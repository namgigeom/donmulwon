# PyInstaller build configuration for DONMULWON.
# Secrets (.env) are intentionally NOT bundled. Keep .env beside the EXE.

from PyInstaller.utils.hooks import collect_submodules

ai_hiddenimports = collect_submodules("ai")

hiddenimports = ai_hiddenimports + [
    "toss_api",
    "market_data",
    "news_data",
    "portfolio",
    "portfolio_data",
    "portfolio_history",
    "change_detector",
    "trade_detector",
    "ai_portfolio",
]


a = Analysis(
    ["main.py"],
    pathex=["."],
    binaries=[],
    datas=[],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="DONMULWON",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
)

# GUI build configuration for DONMULWON.
# Keep .env beside the EXE; secrets are intentionally not bundled.

from PyInstaller.utils.hooks import collect_submodules

hiddenimports = collect_submodules("ai") + [
    "toss_api",
    "market_data",
    "news_data",
    "portfolio",
    "portfolio_data",
    "portfolio_history",
    "change_detector",
    "trade_detector",
    "ai_portfolio",
    "PySide6",
]

a = Analysis(
    ["gui.py"],
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
    console=False,
)

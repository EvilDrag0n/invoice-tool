from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files, collect_submodules


PROJECT_ROOT = Path(SPECPATH).resolve()

# tkinterdnd2 relies on bundled Tk resources that PyInstaller can miss unless
# they are collected explicitly.
datas = collect_data_files("tkinterdnd2")
hiddenimports = collect_submodules("tkinterdnd2")

# Keep the bundle focused on runtime modules used by the GUI path. The clean
# build venv is still the primary size-control mechanism; these excludes only
# trim common accidental pulls.
excludes = [
    "IPython",
    "ipykernel",
    "jedi",
    "matplotlib",
    "notebook",
    "pytest",
    "setuptools",
    "test",
    "tests",
    "unittest",
    "wheel",
]


a = Analysis(
    [str(PROJECT_ROOT / "invoice_tool" / "gui" / "__main__.py")],
    pathex=[str(PROJECT_ROOT)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    name="InvoiceTool",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="InvoiceTool",
)

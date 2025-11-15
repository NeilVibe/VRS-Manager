# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for VRS Manager
Compiles the modular architecture into a single executable.
"""

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('images/vrsmanager.ico', 'images'),  # Include icon in bundle
    ],
    hiddenimports=[
        'openpyxl',
        'openpyxl.cell',
        'openpyxl.cell._writer',
        'openpyxl.styles',
        'openpyxl.styles.stylesheet',
        'openpyxl.styles.colors',
        'openpyxl.worksheet',
        'openpyxl.worksheet._reader',
        'openpyxl.worksheet._write_only',
        'pandas',
        'pandas.io.formats.excel',
        'tkinter',
        'tkinter.scrolledtext',
        'tkinter.ttk',
        # All src modules
        'src',
        'src.config',
        'src.processors',
        'src.processors.base_processor',
        'src.processors.raw_processor',
        'src.processors.working_processor',
        'src.processors.alllang_processor',
        'src.processors.master_processor',
        'src.core',
        'src.core.casting',
        'src.core.lookups',
        'src.core.comparison',
        'src.core.import_logic',
        'src.core.working_comparison',
        'src.core.working_helpers',
        'src.core.alllang_helpers',
        'src.io',
        'src.io.excel_reader',
        'src.io.excel_writer',
        'src.io.formatters',
        'src.io.summary',
        'src.ui',
        'src.ui.main_window',
        'src.ui.history_viewer',
        'src.history',
        'src.history.history_manager',
        'src.utils',
        'src.utils.helpers',
        'src.utils.progress',
        'src.utils.data_processing',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'scipy',
        'numpy.testing',
        'PIL',
        'setuptools',
        'distutils',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='VRSManager',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Show console window for debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='images/vrsmanager.ico',  # Use the icon
)

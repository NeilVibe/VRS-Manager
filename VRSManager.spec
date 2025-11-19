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
        ('docs/VRS_Manager_Process_Guide_EN.xlsx', '.'),  # Include English guide
        ('docs/VRS_Manager_Process_Guide_KR.xlsx', '.'),  # Include Korean guide
        ('Previous/README.txt', 'Previous'),  # Include Previous folder with README
        ('Current/README.txt', 'Current'),  # Include Current folder with README
        ('models/kr-sbert', 'models/kr-sbert'),  # BERT model for StrOrigin analysis (447MB)
    ],
    hiddenimports=[
        # Numpy dependencies (critical for PyInstaller)
        'numpy',
        'numpy.core._multiarray_umath',
        'numpy.core._multiarray_tests',
        'numpy.random.common',
        'numpy.random.bounded_integers',
        'numpy.random.entropy',
        # OpenPyXL
        'openpyxl',
        'openpyxl.cell',
        'openpyxl.cell._writer',
        'openpyxl.styles',
        'openpyxl.styles.stylesheet',
        'openpyxl.styles.colors',
        'openpyxl.worksheet',
        'openpyxl.worksheet._reader',
        'openpyxl.worksheet._write_only',
        # Pandas
        'pandas',
        'pandas.io.formats.excel',
        'pandas._libs.tslibs.timedeltas',
        # Tkinter
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
        'src.utils.strorigin_analysis',
        'src.utils.super_groups',
        # BERT and ML dependencies (from XLSTransfer0225 command)
        'torch',
        'torch._C',
        'torch.nn',
        'torch.optim',
        'tokenizers',
        'transformers',
        'sentence_transformers',
        'sentence_transformers.models',
        'sentence_transformers.util',
        'tqdm',
        'regex',
        'requests',
        'packaging',
        'filelock',
        'huggingface_hub',
        'scipy',
        'scipy.spatial',
        'scipy.spatial.distance',
        'scikit-learn',
        'sklearn',
        'sklearn.metrics',
        'sklearn.metrics.pairwise',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',  # Don't need plotting
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
    [],
    exclude_binaries=True,  # Don't bundle binaries - use COLLECT instead
    name='VRSManager',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # Show console window for debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='images/vrsmanager.ico',  # Use the icon
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='VRSManager',
)

# -*- mode: python ; coding: utf-8 -*-
import os
import pico2d
sdl2dll_path = os.getenv('PYSDL2_DLL_PATH')
a = Analysis(
['main.py'], # <====== 1. 메인 소스 파일을 지정해야 합니다.
pathex=[],
binaries=[(os.path.join(sdl2dll_path, '*.dll'), '.')],
datas=[],
hiddenimports=[],
hookspath=[],
hooksconfig={},
runtime_hooks=[],
excludes=[],
noarchive=False,
optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
pyz,
a.scripts,
a.binaries,
a.datas,
[],
name='ToTheTop', # <====== 2. 생성될 실행 파일 이름을 지정해야 합니다.
debug=False,
bootloader_ignore_signals=False,
strip=False,
upx=True,
upx_exclude=[],
runtime_tmpdir=None,
console=False, # <====== 3. 문제가 발생했을 때 True 로 해서 확인.
disable_windowed_traceback=False,
argv_emulation=False,
target_arch=None,
codesign_identity=None,
entitlements_file=None,
)
# -*- mode: python -*-

block_cipher = None


a = Analysis(['horseAR\\testNoARAction.py'],
             pathex=['C:\\ProgramData\\Anaconda3\\Lib\\site-packages\\PyQt5', 'C:\\HORSEAR', 'C:\\programdata\\anaconda3\\lib\\site-packages\\zmq'],
             binaries=[],
             datas=[('C:\\HORSEAR\\ExtraDLL\\platforms/*.dll', 'platforms' ),
		      ('horseAR\\horseAR.config','config')],
             hiddenimports=['scipy._lib.messagestream'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='HORSEAR TEST',
          debug=False,
          strip=False,
          upx=True,
          console=True,
		  icon='C:\\HORSEAR\\horselogo.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='HORSEAR TEST distribution',
               icon='C:\\HORSEAR\\horselogo.ico')
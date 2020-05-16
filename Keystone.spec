# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['MainWindow.py'],
             pathex=['C:\\Users\\Jock_\\Documents\\GitHub\\Keystone'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas + [
              ('Resources/Keystone.ico', 'Resources/Keystone.ico', 'DATA'),
              ('Resources/LeadBrick1.jpg', 'Resources/LeadBrick1.jpg', 'DATA')
              ],
          [],
          name='Keystone',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False,
          icon='Resources/Keystone.ico' )

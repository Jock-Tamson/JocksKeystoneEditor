import os
from PyInstaller import __main__

workdir = os.getcwd()
spec = os.path.join(workdir, "Keystone.spec")

distdir = os.path.join(workdir, 'dist')
builddir = os.path.join(workdir, 'build')

__main__.run(['--distpath', distdir, '--workpath', builddir, spec])
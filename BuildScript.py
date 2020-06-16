import datetime
import os

from PyInstaller import __main__ as pyi

VERSION = '0.2.2-dev'

if (__name__ == "__main__"):
    workdir = os.getcwd()

    #build version file
    versionPath = os.path.join(workdir, "VERSION.txt")
    version = VERSION + '\nbuild: ' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    print("Writing verson %s to %s" % (version, versionPath))
    file = open(versionPath, "w+")
    try:
        file.write(version)
    finally:
        file.close()

    spec = os.path.join(workdir, "Keystone.spec")

    distdir = os.path.join(workdir, 'dist')
    builddir = os.path.join(workdir, 'build')

    pyi.run(['--distpath', distdir, '--workpath', builddir, spec])

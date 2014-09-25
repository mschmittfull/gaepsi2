from distutils.core import setup
from Cython.Build import cythonize
from distutils.extension import Extension
def myext(*args):
    return Extension(*args, include_dirs=["./"])
extensions = [
        myext("gaepsi.svr", ["src/svr.pyx"]),
        myext("gaepsi.domain", ["src/domain.pyx"]),
        myext("gaepsi.painter", ["src/painter.pyx"])
        ]

setup(
    name="bigfilepy", version="0.1",
    author="Yu Feng",
    description="python binding of BigFile, a peta scale IO format",
    package_dir = {'gaepsi': 'src'},
    install_requires=['cython', 'numpy'],
    packages= ['gaepsi'],
    requires=['numpy'],
    ext_modules = cythonize(extensions)
)

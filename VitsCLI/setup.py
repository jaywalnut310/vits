from distutils.core import setup
from Cython.Build import cythonize

setup(ext_modules=cythonize("cleaner.py"),
      compiler_directives={'language_level': "3"})

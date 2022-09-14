from setuptools.extension import Extension

import numpy
from Cython.Build import cythonize
from Cython.Distutils import build_ext

modules = [
    "vits/monotonic_align/core.pyx",
]

extensions = [
    Extension("vits.monotonic_align.core",
              ["vits/monotonic_align/core.pyx"],
                include_dirs=[numpy.get_include()]
              )
]

class BuildExt(build_ext):
    def build_extensions(self):
        try:
            super().build_extensions()
        except Exception:
            pass

def build(setup_kwargs):
    setup_kwargs.update(
        dict(
            cmdclass=dict(build_ext=BuildExt),
            ext_modules=cythonize(extensions,
                                  language_level=3),
            zip_safe=False
        )
    )
# if __name__ == '__main__':
#     build()
    

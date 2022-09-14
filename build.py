import numpy
from Cython.Build import cythonize

modules = [
    "vits/monotonic_align/core.pyx",
]

extensions = cythonize(modules)


def build(setup_kwargs):
    """
    This is a callback for poetry used to hook in our extensions.
    """

    setup_kwargs.update(
        {
            # declare the extension so that setuptools will compile it
            "name": "monotonic_align",
            "ext_modules": extensions,
            "include_dirs": [numpy.get_include()],
        }
    )
# if __name__ == '__main__':
#     build()
    

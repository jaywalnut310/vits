from distutils.core import setup
from Cython.Build import cythonize

setup(ext_modules=cythonize(
  ["craft_vits.py", "hparams.py", "inference.py", "load_checkpoint.py", "text/symbols.py",
   "text/cleaner.py", "commons.py", "duration_predictor.py", "stochastic_duration_predictor.py",
   "residual_coupling_block.py", "posterior_encoder.py", "generator.py", "text_encoder.py",
   "attentions.py", "modules.py", "transforms.py"],
  compiler_directives={'language_level': "3"}))

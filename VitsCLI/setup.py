import zipfile

with zipfile.PyZipFile("infer.zip", mode="w", compression=zipfile.ZIP_DEFLATED) as pkg:
  pkg.writepy("Infer")

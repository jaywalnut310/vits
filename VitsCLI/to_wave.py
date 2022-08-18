import struct
import sys


class WAVE_FORMAT:
  PCM = 0x0001
  IEEE_FLOAT = 0x0003


def write(filename, rate, data):
  if hasattr(filename, 'write'):
    fid = filename
  else:
    fid = open(filename, 'wb')

  fs = rate

  try:
    dkind = data.dtype.kind
    if not (dkind == 'i' or dkind == 'f' or (dkind == 'u' and
                                             data.dtype.itemsize == 1)):
      raise ValueError("Unsupported data type '%s'" % data.dtype)

    header_data = b''

    header_data += b'RIFF'
    header_data += b'\x00\x00\x00\x00'
    header_data += b'WAVE'

    # fmt chunk
    header_data += b'fmt '
    if dkind == 'f':
      format_tag = WAVE_FORMAT.IEEE_FLOAT
    else:
      format_tag = WAVE_FORMAT.PCM
    if data.ndim == 1:
      channels = 1
    else:
      channels = data.shape[1]
    bit_depth = data.dtype.itemsize * 8
    bytes_per_second = fs * (bit_depth // 8) * channels
    block_align = channels * (bit_depth // 8)

    fmt_chunk_data = struct.pack('<HHIIHH', format_tag, channels, fs,
                                 bytes_per_second, block_align, bit_depth)
    if not (dkind == 'i' or dkind == 'u'):
      # add cbSize field for non-PCM files
      fmt_chunk_data += b'\x00\x00'

    header_data += struct.pack('<I', len(fmt_chunk_data))
    header_data += fmt_chunk_data

    # fact chunk (non-PCM files)
    if not (dkind == 'i' or dkind == 'u'):
      header_data += b'fact'
      header_data += struct.pack('<II', 4, data.shape[0])

    # check data size (needs to be immediately before the data chunk)
    if ((len(header_data) - 4 - 4) + (4 + 4 + data.nbytes)) > 0xFFFFFFFF:
      raise ValueError("Data exceeds wave file size limit")

    fid.write(header_data)

    # data chunk
    fid.write(b'data')
    fid.write(struct.pack('<I', data.nbytes))
    if data.dtype.byteorder == '>' or (data.dtype.byteorder == '=' and
                                       sys.byteorder == 'big'):
      data = data.byteswap()
    fid.write(data.ravel().view('b').data)

    # Determine file size and place it in correct
    #  position at start of the file.
    size = fid.tell()
    fid.seek(4)
    fid.write(struct.pack('<I', size - 8))

  finally:
    if not hasattr(filename, 'write'):
      fid.close()
    else:
      fid.seek(0)

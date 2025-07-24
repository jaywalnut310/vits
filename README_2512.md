1 - First clean the data as needed
2 - if we don have transcriptions, run the script allison_corpora/scripts/audio_processor.py to concatenate all files and split in chunks. otherwise, step to 3
2.1 - run stt in each of the chunks and ensure there only speech
3 - create folder in the vits expected format: dummy1 poining to chunks, and filelists/filelist_train and  filelists/filelist_val
3.1 - preprocess the phonemes as required for the language as described in the "## Pre-requisites" step in the original Readme.
4 - Train the model
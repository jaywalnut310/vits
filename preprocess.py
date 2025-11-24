import argparse
import text
from utils import load_filepaths_and_text

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--out_extension", default="cleaned")
    parser.add_argument("--text_index", default=2, type=int)
    parser.add_argument(
        "--filelists",
        nargs="+",
        default=[
            "/media/4tbdrive/engines/vits/filelists/portuguese_mixed_corpora_train_2512.txt",
            "/media/4tbdrive/engines/vits/filelists/portuguese_mixed_corpora_val_2512.txt",
        ],
    )
    parser.add_argument("--text_cleaners", nargs="+", default=["portuguese_cleaners2"])

    args = parser.parse_args()

    for filelist in args.filelists:
        print("START:", filelist)
        filepaths_and_text = load_filepaths_and_text(filelist)
        for i in range(len(filepaths_and_text)):
            original_text = filepaths_and_text[i][args.text_index]
            cleaned_text = text._clean_text(original_text, args.text_cleaners)
            filepaths_and_text[i][args.text_index] = cleaned_text

        new_filelist = filelist + "." + args.out_extension
        with open(new_filelist, "w", encoding="utf-8") as f:
            f.writelines(["|".join(x) + "\n" for x in filepaths_and_text])

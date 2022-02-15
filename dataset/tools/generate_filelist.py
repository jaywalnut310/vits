# from pathlib import Path
#
#
# def write_filelist(filename, data_lines):
#     open(Path(output_dir) / filename, mode='w').writelines(data_lines)
#
#
# if __name__ == '__main__':
#     dataset_dir = "/media/arnas/SSD Disk/inovoice/unzipped/vits_audiobooks/paulius_ciziniauskas"
#     output_dir = "/media/arnas/SSD Disk/uni/semester_3/master_thesis/repos/vits/filelists"
#     name = "paulius"
#     train_split = 0.9
#     val_test_split = 0.05
#
#     dataset = [example_line for example_line in open(str(Path(dataset_dir) / 'metadata.csv'), mode='r').readlines()]
#     dataset_len = len(dataset)
#     training_example_count = int(dataset_len * train_split)
#     val_test_example_count = int(dataset_len * val_test_split)
#     train_set = dataset[:training_example_count]
#     val_set = dataset[training_example_count:training_example_count + val_test_example_count]
#     test_set = dataset[training_example_count + val_test_example_count:dataset_len]
#
#     write_filelist(f"{name}_train_filelist.txt", train_set)
#     write_filelist(f"{name}_val_filelist.txt", val_set)
#     write_filelist(f"{name}_test_filelist.txt", test_set)

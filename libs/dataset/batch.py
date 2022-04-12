from libs.dataset.core import SampleEntry


def index_entries(starting_idx: int = 0):
    index_entries.idx = starting_idx

    def step(sample_entry: SampleEntry):
        index_entries.idx += 1
        return index_entries.idx, sample_entry

    return step

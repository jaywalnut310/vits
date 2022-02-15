from dataset.core import SampleEntry


def does_not_have_numbers(s: SampleEntry):
    return not any(char.isdigit() for char in s.text)


def waveform_not_longer_than(target_length):
    def step(s: SampleEntry):
        return s.duration < target_length

    return step


def waveform_not_shorter_than(target_length):
    def step(s: SampleEntry):
        return s.duration > target_length

    return step

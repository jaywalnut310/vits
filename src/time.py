from datetime import time


def format_milliseconds_as_srt_time(time_str):
    time_seconds = milliseconds_str_to_time(time_str)
    return time.strftime(time_seconds, "%H:%M:%S,%f")[:-3]


def milliseconds_str_to_time(milliseconds_str):
    milliseconds = int(milliseconds_str)

    seconds = milliseconds // 1000
    minutes = (seconds // 60) % 60
    hours = seconds // 3600

    microseconds = (milliseconds % 1000) * 1000
    seconds = seconds % 60
    return time(hour=hours, minute=minutes, second=seconds, microsecond=microseconds)

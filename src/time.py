import datetime
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


def srt_time_to_millisecond_float(time_str, fmt='%H:%M:%S,%f') -> float:
    dtime = datetime.datetime.strptime(time_str, fmt)
    return dtime.hour * 3600000 + dtime.minute * 60000 + dtime.second * 1000 + dtime.microsecond / 1000

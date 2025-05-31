from datetime import datetime, time, timedelta

def parse_time(time_str: str) -> time:
    return datetime.strptime(time_str, "%H:%M").time()

def time_to_seconds(t: time) -> float:
    return t.hour * 3600 + t.minute * 60 + t.second

def seconds_to_time(seconds: float) -> time:
    total_seconds = int(seconds)
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds_rem = total_seconds % 60
    return time(hours % 24, minutes, seconds_rem)

def add_seconds_to_time(base_time: time, seconds_to_add: float) -> time:
    base_datetime = datetime.combine(datetime.min, base_time)
    new_datetime = base_datetime + timedelta(seconds=seconds_to_add)
    return new_datetime.time()
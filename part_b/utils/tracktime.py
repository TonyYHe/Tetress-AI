import time

def time_left(time_remaining, start_time):
    if time_remaining is not None:
        elapsed_time = time.time() - start_time
        time_remaining -= elapsed_time
        return time_remaining
    return None


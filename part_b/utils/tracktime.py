import time

def time_left(time_remaining, start_time):
    """
    Return the amount of time remaining, where the elapsed time is from the 
    input start time to now.
    """
    if time_remaining is not None:
        elapsed_time = time.time() - start_time
        time_remaining -= elapsed_time
        return time_remaining
    return None


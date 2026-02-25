import datetime

def timestamp_to_datetime(timestamp):
    return datetime.datetime.fromtimestamp(timestamp, tz=datetime.timezone.utc) if timestamp else None
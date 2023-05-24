import datetime


def split_date(date: str, start: str, end: str = None):
    y, m, d = date.split('-')
    ha, ma = start.split(':')
    date_a = datetime.datetime(int(y), int(m), int(d), int(ha), int(ma))
    if end:
        hb, mb = end.split(':')
        date_b = datetime.datetime(int(y), int(m), int(d), int(hb), int(mb))
        return date_a, date_b
    return date_a

def get_time_wib():
    return datetime.datetime.utcnow() + datetime.timedelta(hours=7)

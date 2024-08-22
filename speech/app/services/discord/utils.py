from datetime import datetime

import pytz


def convert_to_minguo_format(timestamp: datetime):
    tz = pytz.timezone('Asia/Taipei')
    local_time = timestamp.astimezone(tz)
    minguo_year = local_time.year - 1911
    return f"民國 {minguo_year} 年 {local_time.month} 月 {local_time.day} 日 {local_time.hour} 點 {local_time.minute} 分"

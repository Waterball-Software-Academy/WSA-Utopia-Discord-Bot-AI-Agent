from datetime import datetime


def convert_to_minguo_format(timestamp: datetime):
    minguo_year = timestamp.year - 1911

    return f"民國 {minguo_year} 年 {timestamp.month} 月 {timestamp.day} 日 {timestamp.hour} 點 {timestamp.minute} 分"

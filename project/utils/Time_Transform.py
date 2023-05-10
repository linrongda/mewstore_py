import datetime


def time_transform(timestamp):
    local_time = timestamp + datetime.timedelta(hours=8)  # 加上8小时是因为中国位于UTC+8时区
    local_time_str = local_time.strftime('%Y-%m-%d %H:%M:%S')
    return local_time_str

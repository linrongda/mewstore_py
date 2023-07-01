# 时间转换，将数据库中的UTC时间转换为北京时间
import datetime


def time_transform(timestamp, is_msg=False):
    local_time = timestamp + datetime.timedelta(hours=8)  # 加上8小时是因为中国位于UTC+8时区
    if is_msg:
        if local_time.date() == datetime.datetime.now().date():
            local_time_str = local_time.strftime('%H:%M')
        elif local_time.year == datetime.datetime.now().year:
            local_time_str = local_time.strftime('%m-%d')
        elif (local_time + datetime.timedelta(days=1)).date() == datetime.datetime.now().date():
            local_time_str = local_time.strftime('昨天')
        else:
            local_time_str = local_time.strftime('%Y-%m-%d')
    else:
        local_time_str = local_time.strftime('%Y-%m-%d %H:%M:%S')
    return local_time_str

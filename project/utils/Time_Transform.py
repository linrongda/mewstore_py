# 时间转换，将数据库中的UTC时间转换为北京时间
import datetime


def time_transform(timestamp, is_msg=False):
    if is_msg:
        if timestamp.date() == datetime.datetime.now().date():
            local_time_str = timestamp.strftime('%H:%M')
        elif (timestamp + datetime.timedelta(days=1)).date() == datetime.datetime.now().date():
            local_time_str = timestamp.strftime('昨天')
        elif timestamp.year == datetime.datetime.now().year:
            local_time_str = timestamp.strftime('%m-%d')
        else:
            local_time_str = timestamp.strftime('%Y-%m-%d')
    else:
        local_time_str = timestamp.strftime('%Y-%m-%d %H:%M:%S')
    return local_time_str

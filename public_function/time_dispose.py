"""
The best sentence

1 Don’t hate your enemy, or you will make wrong judgment.
2 I'm gonna make him an offer he can't refuse.
3 A friend should always underestimate your virtues and an enemy overestimate your faults.
4 You know...the world’s full of lonely people afraid to make the first move
5 I suffer that slight alone,because I’m not accepted by my own people,
    because i’m not like them either! So if I'm not black enough and if I'm not white enough,
    then tell me, Tony, what am I !?
6 whatever you do,do it a hundred percent.when you work,when you laugh,laugh,when you eat,eat like it's your last meal.

@author:StrongXiuXiu
@file:
@time:2021/10/11
"""
import pandas as pd

import datetime


def split_time_ranges(from_time, to_time, frequency):
    # print(from_time,to_time,333444555)
    from_time, to_time = pd.to_datetime(from_time), pd.to_datetime(to_time)
    time_range = list(pd.date_range(from_time, to_time, freq='%sS' % frequency))
    if to_time not in time_range:
        time_range.append(to_time)
    time_range = [item.strftime("%Y-%m-%d %H:%M:%S") for item in time_range]
    time_ranges = []
    for item in time_range:
        f_time = item
        t_time = (datetime.datetime.strptime(item, "%Y-%m-%d %H:%M:%S") + datetime.timedelta(seconds=frequency))
        if t_time >= to_time:
            t_time = to_time.strftime("%Y-%m-%d %H:%M:%S")
            # time_ranges.append(f_time)
            time_ranges.append([f_time, t_time])
            break
        # time_ranges.append(f_time)
        time_ranges.append([f_time, t_time.strftime("%Y-%m-%d %H:%M:%S")])
    # print(len(time_ranges),888888888888888888888888888888888888)
    return time_ranges


if __name__ == '__main__':
    from_time = '2019-10-01 00:00:01'
    to_time = '2019-10-01 06:00:00'
    frequency = 12 * 60 * 60 / 3600
    time_ranges = split_time_ranges(from_time, to_time, frequency)

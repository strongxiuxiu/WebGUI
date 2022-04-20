# asss = "2021-11-23 11:31:06.677409"
# print(asss.strftime('%Y-%m-%d %H:%M:%S'))


import datetime
from dateutil.relativedelta import relativedelta
dd = '2021-12-17 11:00:00'
date = datetime.datetime.strptime(dd, "%Y-%m-%d %H:%M:%S")
#
# d = min(date.day, calendar.monthrange(y, m)[1])

if __name__ == "__main__":
    print(date - relativedelta(months=-1))
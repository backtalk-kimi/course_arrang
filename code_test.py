import pandas as pd
from pandas.tseries.offsets import CustomBusinessDay
import datetime
import numpy as np

# help (CustomBusinessDay)
def count_weekday(s_day, e_day):
    holiday_list = CustomBusinessDay(holidays = ['2021-09-18',
                                                '2021-10-01',
                                                '2021-10-02',
                                                '2021-10-03',
                                                '2021-10-04',
                                                '2021-10-05',
                                                '2021-10-06',
                                                '2021-10-07'])
    # help(CustomBusinessDay)
    bus_day = pd.date_range(start = s_day, end = e_day, freq = 'b')
    # day1 = datetime.datetime.strptime('2021-10-09','%Y-%m-%d')
    # day1 = pd.DatetimeIndex(['2021-10-09'])
    # print(len(bus_day))
    #
    # help(bus_day.intersection)
    # bus_day = bus_day.intersection(bus_day,day1)
    # help(pd.core.indexes.datetimes.DatetimeIndex.join)
    length = len(bus_day)

    print(len(bus_day))
    print(bus_day[0])
    weekday = bus_day[0].weekday() + 1
    print(weekday)

    extra_work_day = ['2021-10-09']
    extra_len = 0
    for i in extra_work_day:
        if s_day <= i <= e_day:
            extra_len = extra_len + 1

    work_data = length + extra_len
    return work_data

# if __name__ == '__main__':
#     count_weekday('2021-9-1', '2022-1-30')
week_mask = str()
week_mask += "Mon"
print(week_mask)
week_on = np.array(7)
print(week_on)
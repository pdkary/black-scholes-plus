from datetime import datetime,timedelta
import re

def get_time_to_expiry(maturity):
    if maturity ==0:
        return 0
    # Today's date
    day_0 = datetime.today()
    # Maturity date
    date_format = "%Y-%m-%d"
    day_exp = datetime.strptime(maturity, date_format)
    # Delta date: i.e. 1 day, 0:00:00
    date_to_exp = day_exp - day_0
    # Delta days: i.e. 1 day
    days_to_exp = date_to_exp.days
    return days_to_exp if days_to_exp > 0 else 0

def get_d_m_y(maturity):
    d = datetime.strptime(maturity,"%Y-%m-%d")
    return (d.day,d.month,d.year)

def interval_to_timedelta(interval:str):
    a = re.search("(\d+)(\w+)",interval)
    val = int(a.group1(1))
    typ = a.group(2)
    if typ=="m":
        return timedelta(minutes=val)
    elif typ=="h":
        return timedelta(hours=val)
    elif typ=="d":
        return timedelta(days=val)
    elif typ=="mo":
        return timedelta(weeks=4*val)
    elif typ=="y":
        return timedelta(weeks=52*val)


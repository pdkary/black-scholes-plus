from datetime import datetime

days_per_period = {"1d":1,"5d":5,"1mo":20,"3mo":60,"6mo":120,"1y":252,"2y":252*2,"5y":252*5,"10y":252*10}
intervals_per_day = {"1m":8*60,"2m":8*30,"5m":8*12,"15m":8*4,"30m":8*2,"1h":8,"1d":1}

def get_time_to_expiry(maturity):
    # Today's date
    day_0 = datetime.today()
    # Maturity date
    date_format = "%Y-%m-%d"
    day_exp = datetime.strptime(maturity, date_format)
    # Delta date: i.e. 1 day, 0:00:00
    date_to_exp = day_exp - day_0
    # Delta days: i.e. 1 day
    days_to_exp = date_to_exp.days
    return days_to_exp

def get_intervals_per_period(period,interval):
    d = days_per_period[period]
    return intervals_per_day[interval]*d

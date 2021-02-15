from datetime import datetime

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

def get_annualization_factor(interval):
    hours_per_day = 8
    days_per_year = 252
    if interval=='1m':
        return days_per_year*hours_per_day*60
    elif interval=='2m':
        return days_per_year*hours_per_day*30
    elif interval=='5m':
        return days_per_year*hours_per_day*12
    elif interval=='30m':
        return days_per_year*hours_per_day*2
    elif interval=='60m':
        return days_per_year*hours_per_day
    elif interval=='90m':
        return days_per_year*hours_per_day*2/3
    elif interval=='1h':
        return days_per_year*hours_per_day
    elif interval=='1d':
        return days_per_year
    elif interval=='5d':
        return days_per_year/5
    elif interval=='1wk':
        return days_per_year/7
    elif interval=='1mo':
        return 12
    elif interval=='3mo':
        return 4

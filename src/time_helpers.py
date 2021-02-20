from datetime import datetime

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
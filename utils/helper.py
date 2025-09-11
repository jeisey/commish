import pytz
from datetime import datetime, timedelta

def check_availability():
    est = pytz.timezone('US/Eastern')
    now_est = datetime.now(est)
    current_hour = now_est.hour
    current_day = now_est.weekday()

    if current_day == 1 and current_hour >= 4:  # Tuesday 4am onwards
        return True, now_est.strftime("%A")
    elif 1 < current_day < 4:  # All day Wednesday and Thursday until 7pm
        return True, now_est.strftime("%A")
    elif current_day == 4 and current_hour < 19:  # Thursday until 7pm
        return True, now_est.strftime("%A")
    else:
        return False, now_est.strftime("%A")

def get_current_week(current_date):
    # 2025 NFL (fantasy) weeks keyed by Tuesday of each week
    date_week_dict = {
        '9/9/2025': 1,  '9/16/2025': 2,  '9/23/2025': 3,  '9/30/2025': 4,
        '10/7/2025': 5, '10/14/2025': 6, '10/21/2025': 7, '10/28/2025': 8,
        '11/4/2025': 9, '11/11/2025': 10,'11/18/2025': 11,'11/25/2025': 12,
        '12/2/2025': 13,'12/9/2025': 14, '12/16/2025': 15,'12/23/2025': 16
    }

    # Convert the string dates to datetime objects
    date_week_dict_converted = {
        datetime.strptime(date_str, '%m/%d/%Y'): week
        for date_str, week in date_week_dict.items()
    }

    # Sort the dates in descending order
    sorted_dates = sorted(date_week_dict_converted.keys(), reverse=True)

    # Iterate through the sorted dates to find the corresponding week number
    for dt in sorted_dates:
        if current_date >= dt:
            return date_week_dict_converted[dt]
    return None  # If current_date is before all mapped dates


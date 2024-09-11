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
    date_week_dict = {
    '9/10/2024': 1, '9/17/2024': 2, '9/24/2024': 3, '10/1/2024': 4,
    '10/8/2024': 5, '10/15/2024': 6, '10/22/2024': 7, '10/29/2024': 8,
    '11/5/2024': 9, '11/12/2024': 10, '11/19/2024': 11, '11/26/2024': 12,
    '12/3/2024': 13, '12/10/2024': 14, '12/17/2024': 15, '12/24/2024': 16
    }
    # Convert the string dates to datetime objects
    date_week_dict_converted = {datetime.strptime(date, '%m/%d/%Y'): week for date, week in date_week_dict.items()}
    
    # Sort the dates in descending order
    sorted_dates = sorted(date_week_dict_converted.keys(), reverse=True)
    
    # Iterate through the sorted dates to find the corresponding week number
    for date in sorted_dates:
        if current_date >= date:
            return date_week_dict_converted[date]
    return None  # If current date is before all the dates in the dictionary

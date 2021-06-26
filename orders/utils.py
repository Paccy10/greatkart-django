import datetime


def generate_order_number(order):
    year = int(datetime.date.today().strftime('%Y'))
    day = int(datetime.date.today().strftime('%d'))
    month = int(datetime.date.today().strftime('%m'))
    date = datetime.date(year, month, day)
    current_date = date.strftime('%Y%m%d')

    return current_date + str(order.id)

from datetime import datetime

def format_end_date(end_date_str):
    format_str = '%Y-%m-%dT%H:%M:%S.%f%z'
    end_date = datetime.strptime(end_date_str, format_str)

    return end_date.strftime('%d/%m/%Y %H:%M')

def validate_bid(current_price, increment, current_bid):
    print(current_bid)
    print(current_price)
    print(increment)
    return current_bid > current_price and (current_bid - current_price) >= increment and (current_bid - current_price) % increment == 0
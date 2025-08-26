from decimal import Decimal

def calculate_expected_move(stock_price, call_price, put_price):
    """
    Calculates the market's expected price move based on the ATM straddle cost.
    """
    # Ensure all inputs are Decimal for precision
    stock_price = Decimal(stock_price)
    call_price = Decimal(call_price)
    put_price = Decimal(put_price)

    if stock_price <= 0:
        return {"error": "Current Stock Price must be a positive number."}
    if call_price < 0:
        return {"error": "ATM Call Option Price cannot be negative."}
    if put_price < 0:
        return {"error": "ATM Put Option Price cannot be negative."}

    # Use Decimal throughout the calculation
    expected_move = call_price + put_price
    expected_percentage = (expected_move / stock_price) if stock_price > 0 else Decimal('0')
    upper_bound = stock_price + expected_move
    lower_bound = stock_price - expected_move

    return {
        "expected_move": expected_move,
        "expected_percentage": expected_percentage,
        "upper_bound": upper_bound,
        "lower_bound": lower_bound
    }

def compare_sell_vs_exercise(stock_price, strike_price, option_premium):
    """
    Compares the profit from selling an in-the-money option vs. exercising it.
    """
    # Ensure all inputs are Decimal for precision
    stock_price = Decimal(stock_price)
    strike_price = Decimal(strike_price)
    option_premium = Decimal(option_premium)

    if stock_price <= 0:
        return {"error": "Current Stock Price must be a positive number."}
    if strike_price <= 0:
        return {"error": "Option Strike Price must be a positive number."}
    if option_premium < 0:
        return {"error": "Option Premium cannot be negative."}

    if stock_price <= strike_price:
        return {"note": "This calculation is for an in-the-money call option (stock price > strike price). If the stock price is less than or equal to the strike price, the option has no intrinsic value to exercise for a call."}

    # Use Decimal throughout the calculation
    profit_from_selling = option_premium
    intrinsic_value = stock_price - strike_price
    profit_from_exercising = intrinsic_value
    extrinsic_value = option_premium - intrinsic_value

    return {
        "profit_from_selling": profit_from_selling,
        "profit_from_exercising": profit_from_exercising,
        "extrinsic_value": extrinsic_value
    }
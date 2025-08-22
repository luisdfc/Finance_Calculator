def calculate_expected_move(stock_price, call_price, put_price):
    """
    Calculates the market's expected price move based on the ATM straddle cost.
    """
    if stock_price <= 0 or call_price < 0 or put_price < 0:
        return {"error": "Prices must be positive numbers."}

    expected_move = call_price + put_price
    expected_percentage = (expected_move / stock_price) if stock_price > 0 else 0
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
    if stock_price <= 0 or strike_price <= 0 or option_premium < 0:
        return {"error": "Prices must be positive numbers."}

    if stock_price <= strike_price:
        return {"note": "This calculation is for an in-the-money call option where the stock price is greater than the strike price."}

    profit_from_selling = option_premium
    intrinsic_value = stock_price - strike_price
    profit_from_exercising = intrinsic_value
    extrinsic_value = option_premium - intrinsic_value

    return {
        "profit_from_selling": profit_from_selling,
        "profit_from_exercising": profit_from_exercising,
        "extrinsic_value": extrinsic_value
    }
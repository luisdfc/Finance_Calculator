from decimal import Decimal, getcontext
import math
import numpy as np
from scipy.stats import norm

# Set precision for Decimal calculations
getcontext().prec = 10

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

def calculate_black_scholes(s, k, t, r, sigma, option_type, market_premium=None):
    """
    Calculates the theoretical price of a European option using the Black-Scholes model.
    s: current stock price, k: strike price, t: time to expiration (in years),
    r: risk-free interest rate (annual), sigma: volatility (annual).
    """
    s = float(s)
    k = float(k)
    t = float(t) / 365 # Convert days to years
    r = float(r) / 100 # Convert percentage to decimal
    sigma = float(sigma) / 100 # Convert percentage to decimal


    if s <= 0 or k <= 0 or t <= 0 or sigma <= 0:
        return {'error': 'All inputs must be positive values.'}
        
    d1 = (math.log(s / k) + (r + 0.5 * sigma ** 2) * t) / (sigma * math.sqrt(t))
    d2 = d1 - sigma * math.sqrt(t)
    
    if option_type == 'call':
        price = (s * norm.cdf(d1) - k * math.exp(-r * t) * norm.cdf(d2))
    elif option_type == 'put':
        price = (k * math.exp(-r * t) * norm.cdf(-d2) - s * norm.cdf(-d1))
    else:
        return {'error': 'Invalid option type selected.'}
    
    result = {'price': price}
    if market_premium is not None:
        market_premium = float(market_premium)
        if market_premium > price:
            result['valuation'] = 'Overvalued'
            result['difference'] = market_premium - price
        else:
            result['valuation'] = 'Undervalued'
            result['difference'] = price - market_premium

    return result


def _solve_for_move_plot(gamma, delta, total_headwind, option_type):
    """Solves the quadratic equation for plotting purposes."""
    a = 0.5 * gamma
    b = delta
    c = total_headwind
    if abs(a) < 1e-9:
        return -c / b if abs(b) > 1e-9 else None

    discriminant = (b**2) - (4 * a * c)
    if discriminant < 0: return None
    sqrt_discriminant = math.sqrt(discriminant)
    move1 = (-b + sqrt_discriminant) / (2 * a)
    move2 = (-b - sqrt_discriminant) / (2 * a)

    if option_type == 'call':
        if move1 >= 0 and move2 >= 0: return min(move1, move2)
        return move1 if move1 >= 0 else move2
    else:
        if move1 <= 0 and move2 <= 0: return max(move1, move2)
        return move2 if move2 <= 0 else move1


def calculate_advanced_breakeven(inputs):
    """Calculates the breakeven stock movement for an options trade and generates chart data."""
    results = {}
    
    # Convert all inputs to float for calculations
    for key, value in inputs.items():
        if isinstance(value, Decimal):
            inputs[key] = float(value)

    total_theta_decay = inputs['theta'] * inputs['days_to_hold']
    total_vega_impact = inputs['vega'] * inputs['expected_iv_change']
    total_headwind = total_theta_decay + total_vega_impact - inputs['bid_ask_spread']
    results.update({'total_headwind': total_headwind, 'total_theta_decay': total_theta_decay, 'total_vega_impact': total_vega_impact, 'bid_ask_spread_cost': inputs['bid_ask_spread']})

    required_move = _solve_for_move_plot(inputs['gamma'], inputs['delta'], total_headwind, inputs['option_type'])

    if required_move is None:
        results['error'] = f"The total cost headwind of €{-total_headwind:.2f} is too high to overcome."
        return results

    results.update({'required_move': required_move, 'target_price': inputs['current_stock_price'] + required_move, 'percent_move': (required_move / inputs['current_stock_price']) * 100})
    
    max_days = int(inputs['days_to_hold']) + 20
    days_range = np.arange(1, max_days + 1)
    percent_moves_np = [((_solve_for_move_plot(inputs['gamma'], inputs['delta'], (inputs['theta'] * d) + total_vega_impact - inputs['bid_ask_spread'], inputs['option_type']) or np.nan) / inputs['current_stock_price']) * 100 for d in days_range]
    
    # Convert numpy types to native Python types for JSON serialization
    percent_moves = [None if np.isnan(p) else float(p) for p in percent_moves_np]


    chart_data = {
        'labels': [int(d) for d in days_range],
        'datasets': [
            {
                'label': 'Required % Move to Breakeven',
                'data': percent_moves,
                'borderColor': 'rgba(79, 70, 229, 1)',
                'backgroundColor': 'rgba(79, 70, 229, 0.2)',
                'fill': True,
                'tension': 0.4,
            }
        ]
    }
    results['chart_data'] = chart_data
    return results
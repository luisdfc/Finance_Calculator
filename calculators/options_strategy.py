from decimal import Decimal, getcontext
import math
import numpy as np
from scipy.stats import norm

# Set precision for Decimal calculations
getcontext().prec = 28 # Increased precision for complex math

def _erf_decimal(x):
    """
    A Decimal-compatible implementation of the error function (erf),
    using the Abramowitz and Stegun approximation. This is a robust way
    to handle the erf calculation without a native Decimal implementation.
    """
    # Constants for the approximation
    a1 = Decimal('0.254829592')
    a2 = Decimal('-0.284496736')
    a3 = Decimal('1.421413741')
    a4 = Decimal('-1.453152027')
    a5 = Decimal('1.061405429')
    p = Decimal('0.3275911')

    sign = Decimal('1')
    if x < 0:
        sign = Decimal('-1')
    x = abs(x)

    t = Decimal('1.0') / (Decimal('1.0') + p * x)
    y = Decimal('1.0') - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * (-x * x).exp()
    return sign * y

def _norm_cdf_decimal(x):
    """
    A Decimal-compatible implementation of the cumulative distribution function for
    the standard normal distribution, now using our custom _erf_decimal function.
    """
    return Decimal('0.5') * (Decimal('1') + _erf_decimal(x / Decimal('2').sqrt()))

def _norm_pdf_decimal(x):
    """
    A Decimal-compatible implementation of the probability density function for
    the standard normal distribution.
    """
    pi = Decimal(math.pi)
    return (-(x**2 / Decimal('2'))).exp() / (Decimal('2') * pi).sqrt()


def calculate_expected_move(stock_price, call_price, put_price):
    """
    Calculates the market's expected price move based on the ATM straddle cost.
    """
    if stock_price <= 0:
        return {"error": "Current Stock Price must be a positive number."}
    if call_price < 0:
        return {"error": "ATM Call Option Price cannot be negative."}
    if put_price < 0:
        return {"error": "ATM Put Option Price cannot be negative."}

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
    if stock_price <= 0:
        return {"error": "Current Stock Price must be a positive number."}
    if strike_price <= 0:
        return {"error": "Option Strike Price must be a positive number."}
    if option_premium < 0:
        return {"error": "Option Premium cannot be negative."}
    if stock_price <= strike_price:
        return {"note": "This calculation is for an in-the-money call option (stock price > strike price). If the stock price is less than or equal to the strike price, the option has no intrinsic value to exercise for a call."}

    profit_from_selling = option_premium
    intrinsic_value = stock_price - strike_price
    profit_from_exercising = intrinsic_value
    extrinsic_value = option_premium - intrinsic_value

    return {
        "profit_from_selling": profit_from_selling,
        "profit_from_exercising": profit_from_exercising,
        "extrinsic_value": extrinsic_value
    }
    
def binomial_american_option(s, k, t, r, sigma, option_type, steps=100):
    """
    Calculates the price of an American option using the Binomial Tree model, now with Decimal precision.
    """
    if s <= 0 or k <= 0 or t <= 0 or sigma <= 0:
        return {'error': 'All inputs must be positive values for the Binomial model.'}

    t_years = t / Decimal('365')
    r_dec = r / Decimal('100')
    sigma_dec = sigma / Decimal('100')
    
    dt = t_years / steps
    u = (sigma_dec * dt.sqrt()).exp()
    d = Decimal('1') / u
    p = ((r_dec * dt).exp() - d) / (u - d)

    st = [s * (u ** (steps - i)) * (d ** i) for i in range(steps + 1)]

    if option_type == 'call':
        option_values = [max(price - k, Decimal('0')) for price in st]
    else: # put
        option_values = [max(k - price, Decimal('0')) for price in st]

    for i in range(steps - 1, -1, -1):
        for j in range(i + 1):
            option_values[j] = (p * option_values[j] + (Decimal('1') - p) * option_values[j + 1]) * (-r_dec * dt).exp()
            st_price = s * (u ** (i - j)) * (d ** j)
            if option_type == 'call':
                option_values[j] = max(option_values[j], st_price - k)
            else: # put
                option_values[j] = max(option_values[j], k - st_price)

    return {'price': option_values[0]}


def calculate_black_scholes(s, k, t, r, sigma, option_type, market_premium=None, style='european'):
    """
    Calculates the theoretical price of an option and its Greeks with Decimal precision.
    """
    if style == 'american':
        return binomial_american_option(s, k, t, r, sigma, option_type)

    if s <= 0 or k <= 0 or t <= 0 or r < 0 or sigma <= 0:
        return {'error': 'For European options, all inputs must be positive (except risk-free rate).'}

    t_years = t / Decimal('365')
    r_dec = r / Decimal('100')
    sigma_dec = sigma / Decimal('100')

    d1 = ((s / k).ln() + (r_dec + Decimal('0.5') * sigma_dec ** 2) * t_years) / (sigma_dec * t_years.sqrt())
    d2 = d1 - sigma_dec * t_years.sqrt()

    if option_type == 'call':
        price = s * _norm_cdf_decimal(d1) - k * (-r_dec * t_years).exp() * _norm_cdf_decimal(d2)
        delta = _norm_cdf_decimal(d1)
        theta = -(s * _norm_pdf_decimal(d1) * sigma_dec) / (Decimal('2') * t_years.sqrt()) - r_dec * k * (-r_dec * t_years).exp() * _norm_cdf_decimal(d2)
    elif option_type == 'put':
        price = k * (-r_dec * t_years).exp() * _norm_cdf_decimal(-d2) - s * _norm_cdf_decimal(-d1)
        delta = _norm_cdf_decimal(d1) - Decimal('1')
        theta = -(s * _norm_pdf_decimal(d1) * sigma_dec) / (Decimal('2') * t_years.sqrt()) + r_dec * k * (-r_dec * t_years).exp() * _norm_cdf_decimal(-d2)
    else:
        return {'error': 'Invalid option type selected.'}

    gamma = _norm_pdf_decimal(d1) / (s * sigma_dec * t_years.sqrt())
    vega = s * _norm_pdf_decimal(d1) * t_years.sqrt()
    rho = k * t_years * (-r_dec * t_years).exp() * _norm_cdf_decimal(d2) if option_type == 'call' else -k * t_years * (-r_dec * t_years).exp() * _norm_cdf_decimal(-d2)

    result = {
        'price': price,
        'greeks': { 'delta': delta, 'gamma': gamma, 'theta': theta / 365, 'vega': vega / 100, 'rho': rho / 100 }
    }
    
    if market_premium is not None:
        if market_premium > price:
            result['valuation'] = 'Overvalued'
            result['difference'] = market_premium - price
        else:
            result['valuation'] = 'Undervalued'
            result['difference'] = price - market_premium

    price_range = np.linspace(float(s) * 0.7, float(s) * 1.3, 100)
    if option_type == 'call':
        profit_loss = [max(p - float(k), 0) - float(price) for p in price_range]
    else:
        profit_loss = [max(float(k) - p, 0) - float(price) for p in price_range]
    
    result['pl_chart_data'] = {
        'labels': [float(p) for p in price_range],
        'datasets': [{'label': 'Profit/Loss at Expiration', 'data': profit_loss, 'borderColor': ['rgba(255, 99, 132, 1)' if pl < 0 else 'rgba(75, 192, 192, 1)' for pl in profit_loss], 'backgroundColor': ['rgba(255, 99, 132, 0.2)' if pl < 0 else 'rgba(75, 192, 192, 0.2)' for pl in profit_loss], 'fill': False, 'tension': 0.1, }]
    }
    return result

def calculate_implied_volatility(s, k, t, r, market_premium, option_type, style='european'):
    """
    Calculates the implied volatility using a binary search (bisection) method.
    """
    low_vol = Decimal('0.001')
    high_vol = Decimal('5.0')
    
    for i in range(100):
        mid_vol = (low_vol + high_vol) / 2
        price_at_mid_vol = calculate_black_scholes(s, k, t, r, mid_vol * 100, option_type, style=style)['price']
        
        if price_at_mid_vol < market_premium:
            low_vol = mid_vol
        else:
            high_vol = mid_vol
            
        if abs(high_vol - low_vol) < Decimal('0.0001'):
            break
            
    implied_vol = (low_vol + high_vol) / 2
    return {'implied_volatility': implied_vol}

def calculate_advanced_breakeven(inputs):
    """
    Calculates the breakeven stock movement with robust input validation.
    """
    required_keys = ['current_stock_price', 'delta', 'gamma', 'theta', 'vega', 'bid_ask_spread', 'expected_iv_change', 'days_to_hold', 'option_type']
    for key in required_keys:
        if key not in inputs:
            return {"error": f"Missing required input: {key}"}
    
    # Specific validations for values
    if inputs['gamma'] <= 0: return {"error": "Gamma must be a positive value."}
    if inputs['theta'] > 0: return {"error": "Theta must be a negative value for long options."}
    if inputs['days_to_hold'] <= 0: return {"error": "Days to Hold must be a positive number."}

    # Convert to float for numpy/math operations after validation
    for key, value in inputs.items():
        if isinstance(value, Decimal):
            inputs[key] = float(value)

    total_theta_decay = inputs['theta'] * inputs['days_to_hold']
    total_vega_impact = inputs['vega'] * inputs['expected_iv_change']
    total_headwind = total_theta_decay + total_vega_impact - inputs['bid_ask_spread']
    
    results = {'total_headwind': total_headwind, 'total_theta_decay': total_theta_decay, 'total_vega_impact': total_vega_impact, 'bid_ask_spread_cost': inputs['bid_ask_spread']}

    required_move = _solve_for_move_plot(inputs['gamma'], inputs['delta'], total_headwind, inputs['option_type'])
    if required_move is None:
        return {"error": f"The total cost headwind of €{-total_headwind:.2f} is too high to overcome with the given greeks."}

    results.update({'required_move': required_move, 'target_price': inputs['current_stock_price'] + required_move, 'percent_move': (required_move / inputs['current_stock_price']) * 100})
    
    max_days = int(inputs['days_to_hold']) + 20
    days_range = np.arange(1, max_days + 1)
    percent_moves_np = [((_solve_for_move_plot(inputs['gamma'], inputs['delta'], (inputs['theta'] * d) + total_vega_impact - inputs['bid_ask_spread'], inputs['option_type']) or np.nan) / inputs['current_stock_price']) * 100 for d in days_range]
    percent_moves = [None if np.isnan(p) else float(p) for p in percent_moves_np]

    results['chart_data'] = {
        'labels': [int(d) for d in days_range],
        'datasets': [{'label': 'Required % Move to Breakeven', 'data': percent_moves, 'borderColor': 'rgba(79, 70, 229, 1)', 'backgroundColor': 'rgba(79, 70, 229, 0.2)', 'fill': True, 'tension': 0.4 }]
    }
    return results

def _solve_for_move_plot(gamma, delta, total_headwind, option_type):
    """Solves the quadratic equation for plotting purposes."""
    a = 0.5 * gamma
    b = delta
    c = total_headwind
    if abs(a) < 1e-9: return -c / b if abs(b) > 1e-9 else None
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
# calculators/compound_interest.py

from decimal import Decimal, getcontext
import math

# Set precision for Decimal calculations
getcontext().prec = 10

def round_decimal(value, precision=2):
    """Rounds a Decimal value to a specified number of decimal places."""
    return value.quantize(Decimal(f'1e-{precision}'))

def calculate_future_value(principal, annual_rate, years, periods_per_year, periodic_deposit, deposit_at_beginning):
    """
    Calculates the future value of an investment with periodic deposits.
    All inputs are expected to be Decimal for precision.
    """
    principal = Decimal(principal)
    annual_rate = Decimal(annual_rate)
    periodic_deposit = Decimal(periodic_deposit)
    years_dec = Decimal(years) # Use Decimal for years in FV calculation for consistency
    periods_per_year_dec = Decimal(periods_per_year)

    if periods_per_year_dec == 0:
        # Avoid division by zero, treat as simple interest if no compounding periods
        # This case generally implies periods_per_year should be at least 1 for compound interest
        # For simplicity, if no compounding, deposits just add up.
        if annual_rate == 0:
            return principal + (periodic_deposit * years_dec)
        else:
            # If annual_rate > 0 but periods_per_year == 0, this is an undefined scenario for typical compound interest
            # We'll return an error or handle it as simple interest on principal only
            return principal * (Decimal('1') + (annual_rate / Decimal('100')) * years_dec) + (periodic_deposit * years_dec)

    rate_per_period = (annual_rate / Decimal('100')) / periods_per_year_dec
    num_periods = years_dec * periods_per_year_dec

    # Future value of initial principal
    fv_principal = principal * ((Decimal('1') + rate_per_period) ** num_periods)

    # Future value of periodic deposits (annuity)
    if rate_per_period > 0:
        # Annuity formula for future value
        fv_deposits = periodic_deposit * (((Decimal('1') + rate_per_period) ** num_periods - Decimal('1')) / rate_per_period)
        if deposit_at_beginning:
            fv_deposits *= (Decimal('1') + rate_per_period)
    else:
        # If no interest, it's just the sum of deposits
        fv_deposits = periodic_deposit * num_periods
        
    return fv_principal + fv_deposits

def _generate_compound_history(principal, annual_rate, years, periods_per_year, periodic_deposit, deposit_at_beginning, goal_balance=None):
    """
    Generates data for a chart in a Chart.js-friendly format, given all parameters.
    All inputs are expected to be Decimal.
    """
    history = []
    
    # Ensure years is treated as a Decimal for internal calculations
    years_dec = Decimal(years)
    
    # Initialize values for the first year (year 0)
    history.append({
        'year': 0,
        'balance': principal,
        'principal_component': principal,
        'total_deposits_component': Decimal('0'),
        'interest_earned_component': Decimal('0')
    })

    current_principal = principal
    current_deposits = Decimal('0')

    for year_idx in range(1, int(years_dec) + 1):
        # Calculate balance components year by year
        # This approach is more accurate for component breakdown over time
        
        # Balance from previous year's principal and deposits
        previous_balance = history[-1]['balance']

        # Apply interest to the previous balance for the current year
        balance_from_interest = previous_balance * ((Decimal('1') + (annual_rate / Decimal('100')) / periods_per_year) ** periods_per_year)

        # Add deposits for the current year
        deposits_this_year = periodic_deposit * periods_per_year
        
        # Calculate balance at the end of the current year
        # Note: This is an approximation for the graph. For exact FV, use calculate_future_value
        # For the graph components, we'll try to disentangle them.

        # Recalculate components based on the _current year's_ contribution to each component
        # This is a cumulative sum of contributions to the components
        
        # For simplicity in graph, we'll use the 'final balance' logic for each year's total balance,
        # and then back-calculate components for visualization purposes, ensuring consistency with FV formula.
        
        balance = calculate_future_value(principal, annual_rate, Decimal(year_idx), periods_per_year, periodic_deposit, deposit_at_beginning)
        
        total_deposits_component_current_year = periodic_deposit * periods_per_year * Decimal(year_idx)
        
        # The initial principal component remains the original principal value
        principal_component_for_graph = principal

        # Interest is the total balance minus initial principal and total deposits
        interest_earned_component_current_year = balance - principal_component_for_graph - total_deposits_component_current_year

        # Ensure no negative interest if balance is less than principal + deposits due to rounding or low initial values
        interest_earned_component_current_year = max(Decimal('0'), interest_earned_component_current_year)

        history.append({
            'year': year_idx,
            'balance': balance,
            'principal_component': principal_component_for_graph,
            'total_deposits_component': total_deposits_component_current_year,
            'interest_earned_component': interest_earned_component_current_year
        })
        
        if goal_balance is not None and balance >= goal_balance:
            # If a goal is set and reached, stop generating history
            break
    
    return history

def calculate_final_balance_and_history(principal, annual_rate, years, periods_per_year, periodic_deposit, deposit_at_beginning):
    """
    Calculates final balance and generates data for a chart.
    """
    principal = Decimal(principal)
    periodic_deposit = Decimal(periodic_deposit)
    annual_rate = Decimal(annual_rate)
    years = Decimal(years)
    periods_per_year = Decimal(periods_per_year)

    if principal < 0: return {"error": "Initial Balance must be zero or positive."}
    if periodic_deposit < 0: return {"error": "Periodic Deposit must be zero or positive."}
    if annual_rate < 0: return {"error": "Annual Interest Rate must be zero or positive."}
    if years <= 0: return {"error": "Duration (Years) must be a positive number."}
    if periods_per_year <= 0: return {"error": "Deposit Frequency must be at least once a year."}

    history = _generate_compound_history(principal, annual_rate, years, periods_per_year, periodic_deposit, deposit_at_beginning)
    
    if not history: # Handle cases where history generation might fail for invalid inputs
        return {"error": "Could not generate calculation history. Please check your inputs."}

    final_result = history[-1]
    
    # Prepare data in a Chart.js-friendly format
    chart_data = {
        'labels': [str(h['year']) for h in history],
        'datasets': [
            {
                'label': 'Initial Principal',
                'data': [float(round_decimal(h['principal_component'], 2)) for h in history],
                'backgroundColor': 'rgba(59, 130, 246, 0.7)', # Blue
                'borderColor': 'rgba(59, 130, 246, 1)',
                'borderWidth': 1
            },
            {
                'label': 'Total Deposits',
                'data': [float(round_decimal(h['total_deposits_component'], 2)) for h in history],
                'backgroundColor': 'rgba(16, 185, 129, 0.7)', # Green
                'borderColor': 'rgba(16, 185, 129, 1)',
                'borderWidth': 1
            },
            {
                'label': 'Interest Earned',
                'data': [float(round_decimal(h['interest_earned_component'], 2)) for h in history],
                'backgroundColor': 'rgba(245, 158, 11, 0.7)', # Amber
                'borderColor': 'rgba(245, 158, 11, 1)',
                'borderWidth': 1
            }
        ]
    }

    return {
        "final_balance": round_decimal(final_result['balance'], 2),
        "principal": round_decimal(principal, 2),
        "total_deposits": round_decimal(final_result['total_deposits_component'], 2),
        "interest_earned": round_decimal(final_result['interest_earned_component'], 2),
        "chart_data": chart_data,
        "calculated_field": "final_balance"
    }


def calculate_time_to_reach_goal(principal, annual_rate, periodic_deposit, periods_per_year, deposit_at_beginning, goal_balance):
    """
    Calculates the years needed to reach a goal balance using binary search.
    All inputs are expected to be Decimal.
    """
    principal = Decimal(principal)
    annual_rate = Decimal(annual_rate)
    periodic_deposit = Decimal(periodic_deposit)
    periods_per_year = Decimal(periods_per_year)
    goal_balance = Decimal(goal_balance)

    if principal < 0 or periodic_deposit < 0 or annual_rate < 0 or periods_per_year <= 0 or goal_balance <= 0:
        return {"error": "All numeric inputs must be positive or zero (except for frequency, which must be positive). Goal balance must be positive."}
    
    # Edge case: If goal is already met or impossible without interest/deposits
    fv_at_zero_rate_deposits = calculate_future_value(principal, Decimal('0'), Decimal('1'), periods_per_year, periodic_deposit, deposit_at_beginning)
    if principal >= goal_balance:
        return {"note": "Your initial balance already meets or exceeds your goal. No additional time is needed."}
        
    if annual_rate == 0 and periodic_deposit == 0:
        return {"error": "With zero interest and zero periodic deposits, goal is unreachable without more capital."}

    # If only initial principal and goal > initial, and annual_rate = 0, and periodic_deposit = 0: unreachable
    if annual_rate == 0 and periodic_deposit == 0 and principal < goal_balance:
        return {"error": "With zero interest and zero periodic deposits, and current balance below goal, the goal is unreachable."}
    
    # If the growth rate is very low, or it's zero and deposits are also zero, it might be impossible
    if annual_rate == 0 and periodic_deposit > 0:
        # Simple growth: goal_balance = principal + (periodic_deposit * periods_per_year * years)
        # years = (goal_balance - principal) / (periodic_deposit * periods_per_year)
        if (periodic_deposit * periods_per_year) <= 0:
             return {"error": "Cannot reach goal with zero interest and zero or negative total annual deposits."}
        
        required_years = (goal_balance - principal) / (periodic_deposit * periods_per_year)
        if required_years <= 0:
            return {"note": "Your initial balance already meets or exceeds your goal. No time is needed."}
        
        # If goal is reachable, generate history for this fixed number of years
        history = _generate_compound_history(principal, annual_rate, required_years, periods_per_year, periodic_deposit, deposit_at_beginning, goal_balance=goal_balance)
        final_fv = calculate_future_value(principal, annual_rate, required_years, periods_per_year, periodic_deposit, deposit_at_beginning)

        return {
            "years": round_decimal(required_years, 2),
            "final_balance": round_decimal(final_fv, 2),
            "chart_data": _format_chart_data(history),
            "calculated_field": "years"
        }

    low_years = Decimal('0')
    high_years = Decimal('500') # Max 500 years to prevent infinite loop for very distant goals.

    # Binary search for years. Iterate a fixed number of times for precision.
    for _ in range(150): # Increased iterations for better precision
        mid_years = (low_years + high_years) / Decimal('2')
        
        if mid_years == low_years or mid_years == high_years: # Prevent infinite loop if values converge too slowly
            break
        
        fv = calculate_future_value(principal, annual_rate, mid_years, periods_per_year, periodic_deposit, deposit_at_beginning)
        
        if fv < goal_balance:
            low_years = mid_years
        else:
            high_years = mid_years
            
    final_years = high_years # High_years will be the first value to exceed goal
    
    if final_years >= high_years: # If it hits max years, it might be unreachable
        fv_at_max_years = calculate_future_value(principal, annual_rate, high_years, periods_per_year, periodic_deposit, deposit_at_beginning)
        if fv_at_max_years < goal_balance:
            return {"error": f"Goal of €{round_decimal(goal_balance, 2):,.2f} unreachable within {int(high_years)} years with given inputs. Consider increasing deposit/initial balance/interest rate."}

    # Generate history for the chart based on the calculated years
    # Ensure years for history generation is an int or Decimal that can be iterated for years
    history_years = math.ceil(float(final_years)) # Ensure we plot full years up to the point of reaching goal
    history = _generate_compound_history(principal, annual_rate, Decimal(history_years), periods_per_year, periodic_deposit, deposit_at_beginning, goal_balance=goal_balance)
    
    final_fv = calculate_future_value(principal, annual_rate, final_years, periods_per_year, periodic_deposit, deposit_at_beginning)

    return {
        "years": round_decimal(final_years, 2),
        "final_balance": round_decimal(final_fv, 2),
        "chart_data": _format_chart_data(history),
        "calculated_field": "years"
    }

def calculate_periodic_deposit_needed(principal, annual_rate, years, periods_per_year, deposit_at_beginning, goal_balance):
    """
    Calculates the periodic deposit needed to reach a goal balance.
    All inputs are expected to be Decimal.
    """
    principal = Decimal(principal)
    annual_rate = Decimal(annual_rate)
    years_dec = Decimal(years)
    periods_per_year_dec = Decimal(periods_per_year)
    goal_balance = Decimal(goal_balance)

    if principal < 0 or annual_rate < 0 or years_dec <= 0 or periods_per_year_dec <= 0 or goal_balance <= 0:
        return {"error": "All numeric inputs must be positive or zero (except for frequency, which must be positive). Goal balance must be positive."}

    # Calculate FV of initial principal
    rate_per_period = (annual_rate / Decimal('100')) / periods_per_year_dec
    num_periods = years_dec * periods_per_year_dec
    fv_principal_only = principal * ((Decimal('1') + rate_per_period) ** num_periods)

    if fv_principal_only >= goal_balance:
        return {"note": f"Your initial principal (€{round_decimal(principal, 2):,.2f}) already grows to €{round_decimal(fv_principal_only, 2):,.2f}, which meets or exceeds your goal of €{round_balance(goal_balance, 2):,.2f} without any periodic deposits. Required deposit is €0.00."}

    # Remaining future value needed from deposits
    required_fv_from_deposits = goal_balance - fv_principal_only

    # Calculate PMT (periodic deposit)
    if rate_per_period > 0:
        denominator = ((Decimal('1') + rate_per_period) ** num_periods - Decimal('1')) / rate_per_period
        if deposit_at_beginning:
            denominator *= (Decimal('1') + rate_per_period)
        
        if denominator <= 0: # This means the growth from deposits is zero or negative, which shouldn't happen with positive rate.
            return {"error": "Cannot calculate required periodic deposit due to a mathematical impossibility or insufficient growth from initial principal."}
        
        required_deposit = required_fv_from_deposits / denominator
    else: # rate_per_period == 0
        if num_periods <= 0:
            return {"error": "Cannot calculate required periodic deposit because the duration is too short or the frequency is invalid."}
        required_deposit = required_fv_from_deposits / num_periods
    
    if required_deposit < 0:
        return {"note": f"Your initial principal already grows to €{round_decimal(fv_principal_only, 2):,.2f}, which exceeds your goal of €{round_decimal(goal_balance, 2):,.2f}. No periodic deposit is needed (or a withdrawal is implied, which is not supported)."}
        
    # Generate history for the chart based on the calculated periodic deposit
    history = _generate_compound_history(principal, annual_rate, years, periods_per_year, required_deposit, deposit_at_beginning)

    final_fv = calculate_future_value(principal, annual_rate, years, periods_per_year, required_deposit, deposit_at_beginning)
    
    return {
        "periodic_deposit": round_decimal(required_deposit, 2),
        "final_balance": round_decimal(final_fv, 2),
        "chart_data": _format_chart_data(history),
        "calculated_field": "periodic_deposit"
    }

def calculate_interest_rate_needed(principal, years, periods_per_year, periodic_deposit, deposit_at_beginning, goal_balance):
    """
    Calculates the annual interest rate needed to reach a goal balance using binary search.
    All inputs are expected to be Decimal.
    """
    principal = Decimal(principal)
    years_dec = Decimal(years)
    periodic_deposit = Decimal(periodic_deposit)
    periods_per_year_dec = Decimal(periods_per_year)
    goal_balance = Decimal(goal_balance)

    if principal < 0 or periodic_deposit < 0 or years_dec <= 0 or periods_per_year_dec <= 0 or goal_balance <= 0:
        return {"error": "All numeric inputs must be positive or zero (except for frequency, which must be positive). Goal balance must be positive."}
    
    # Edge case: If goal is already met or impossible without interest
    fv_at_zero_rate = calculate_future_value(principal, Decimal('0'), years_dec, periods_per_year_dec, periodic_deposit, deposit_at_beginning)
    if fv_at_zero_rate >= goal_balance:
        return {"note": f"Your investment reaches €{round_decimal(fv_at_zero_rate, 2):,.2f} with 0% interest, already meeting or exceeding your goal of €{round_decimal(goal_balance, 2):,.2f}. Required annual interest rate is 0.00%."}
    
    # If no principal and no deposits, cannot reach goal with any interest rate.
    if principal == 0 and periodic_deposit == 0 and goal_balance > 0:
        return {"error": "With zero initial balance and zero periodic deposits, a positive interest rate alone cannot grow the investment to a positive goal."}
        
    # If fv_at_zero_rate is still less than goal_balance, we need a positive rate.
    
    low_rate = Decimal('0')
    high_rate = Decimal('500') # Search up to 500% annual rate (very high but covers most scenarios)

    # Binary search for annual_rate
    for _ in range(150): # Increased iterations for better precision
        mid_rate = (low_rate + high_rate) / Decimal('2')
        
        if mid_rate == low_rate or mid_rate == high_rate: # Prevent infinite loop if values converge too slowly
            break

        fv = calculate_future_value(principal, mid_rate, years_dec, periods_per_year_dec, periodic_deposit, deposit_at_beginning)

        if fv < goal_balance:
            low_rate = mid_rate
        else:
            high_rate = mid_rate
            
    final_rate = high_rate # High_rate will be the first value to exceed goal
    
    if final_rate >= high_rate: # If it hits max rate, it might be unreachable
        fv_at_max_rate = calculate_future_value(principal, high_rate, years_dec, periods_per_year_dec, periodic_deposit, deposit_at_beginning)
        if fv_at_max_rate < goal_balance:
            return {"error": f"Goal of €{round_decimal(goal_balance, 2):,.2f} unreachable with an annual interest rate up to {float(round_decimal(high_rate, 2)):.2f}%."}

    # Generate history for the chart based on the calculated interest rate
    history = _generate_compound_history(principal, final_rate, years, periods_per_year, periodic_deposit, deposit_at_beginning)

    final_fv = calculate_future_value(principal, final_rate, years, periods_per_year, periodic_deposit, deposit_at_beginning)
    
    return {
        "interest_rate": round_decimal(final_rate, 2),
        "final_balance": round_decimal(final_fv, 2),
        "chart_data": _format_chart_data(history),
        "calculated_field": "interest_rate"
    }


def calculate_initial_balance_needed(annual_rate, years, periods_per_year, periodic_deposit, deposit_at_beginning, goal_balance):
    """
    Calculates the initial balance needed to reach a goal balance.
    All inputs are expected to be Decimal.
    """
    annual_rate = Decimal(annual_rate)
    years_dec = Decimal(years)
    periodic_deposit = Decimal(periodic_deposit)
    periods_per_year_dec = Decimal(periods_per_year)
    goal_balance = Decimal(goal_balance)

    if periodic_deposit < 0 or annual_rate < 0 or years_dec <= 0 or periods_per_year_dec <= 0 or goal_balance <= 0:
        return {"error": "All numeric inputs must be positive or zero (except for frequency, which must be positive). Goal balance must be positive."}

    rate_per_period = (annual_rate / Decimal('100')) / periods_per_year_dec
    num_periods = years_dec * periods_per_year_dec

    # Calculate FV of periodic deposits
    if rate_per_period > 0:
        fv_deposits = periodic_deposit * (((Decimal('1') + rate_per_period) ** num_periods - Decimal('1')) / rate_per_period)
        if deposit_at_beginning:
            fv_deposits *= (Decimal('1') + rate_per_period)
    else: # rate_per_period == 0
        fv_deposits = periodic_deposit * num_periods

    # Future value needed from initial principal component
    required_fv_from_principal = goal_balance - fv_deposits

    if required_fv_from_principal <= 0:
        return {"note": f"Your periodic deposits (€{round_decimal(periodic_deposit, 2):,.2f}) already grow to €{round_decimal(fv_deposits, 2):,.2f}, which meets or exceeds your goal of €{round_decimal(goal_balance, 2):,.2f}. No initial balance is needed."}

    # Calculate required initial principal (P)
    # FV_principal = P * (1 + r/n)^nt  => P = FV_principal / (1 + r/n)^nt
    compound_factor = (Decimal('1') + rate_per_period) ** num_periods
    
    if compound_factor == 0:
         return {"error": "Cannot calculate required initial balance due to mathematical impossibility (compound factor is zero)."}
         
    required_principal = required_fv_from_principal / compound_factor
    
    if required_principal < 0:
        # This implies that the deposits alone would exceed the goal, so a negative principal is needed
        # which is not a valid scenario for "initial balance needed"
        return {"note": f"Your periodic deposits already exceed the goal of €{round_decimal(goal_balance, 2):,.2f}. No initial balance is needed (a withdrawal from principal would be implied)."}


    # Generate history for the chart based on the calculated initial balance
    history = _generate_compound_history(required_principal, annual_rate, years, periods_per_year, periodic_deposit, deposit_at_beginning)
    
    final_fv = calculate_future_value(required_principal, annual_rate, years, periods_per_year, periodic_deposit, deposit_at_beginning)

    return {
        "initial_balance": round_decimal(required_principal, 2),
        "final_balance": round_decimal(final_fv, 2),
        "chart_data": _format_chart_data(history),
        "calculated_field": "initial_balance"
    }

def _format_chart_data(history):
    """Helper to format chart data from history for consistency."""
    return {
        'labels': [str(h['year']) for h in history],
        'datasets': [
            {
                'label': 'Initial Principal',
                'data': [float(round_decimal(h['principal_component'], 2)) for h in history],
                'backgroundColor': 'rgba(59, 130, 246, 0.7)', # Blue
                'borderColor': 'rgba(59, 130, 246, 1)',
                'borderWidth': 1
            },
            {
                'label': 'Total Deposits',
                'data': [float(round_decimal(h['total_deposits_component'], 2)) for h in history],
                'backgroundColor': 'rgba(16, 185, 129, 0.7)', # Green
                'borderColor': 'rgba(16, 185, 129, 1)',
                'borderWidth': 1
            },
            {
                'label': 'Interest Earned',
                'data': [float(round_decimal(h['interest_earned_component'], 2)) for h in history],
                'backgroundColor': 'rgba(245, 158, 11, 0.7)', # Amber
                'borderColor': 'rgba(245, 158, 11, 1)',
                'borderWidth': 1
            }
        ]
    }

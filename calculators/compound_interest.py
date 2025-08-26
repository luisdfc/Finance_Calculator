# calculators/compound_interest.py (Updated for multi-goal calculations)

from decimal import Decimal, getcontext
import math

# Set precision for Decimal calculations
getcontext().prec = 10

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
        # Simple sum if no compounding periods
        return principal + (periodic_deposit * years_dec * periods_per_year_dec) # Should be 0 if periods_per_year_dec is 0

    rate_per_period = (annual_rate / Decimal('100')) / periods_per_year_dec
    num_periods = years_dec * periods_per_year_dec

    # Future value of initial principal
    fv_principal = principal * ((Decimal('1') + rate_per_period) ** num_periods)

    # Future value of periodic deposits (annuity)
    if rate_per_period > 0:
        fv_deposits = periodic_deposit * (((Decimal('1') + rate_per_period) ** num_periods - Decimal('1')) / rate_per_period)
        if deposit_at_beginning:
            fv_deposits *= (Decimal('1') + rate_per_period)
    else:
        # If no interest, it's just the sum of deposits
        fv_deposits = periodic_deposit * num_periods
        
    return fv_principal + fv_deposits

def _generate_compound_history(principal, annual_rate, years, periods_per_year, periodic_deposit, deposit_at_beginning):
    """
    Generates data for a chart in a Chart.js-friendly format, given all parameters.
    All inputs are expected to be Decimal.
    """
    history = []
    
    # Initialize values for the first year (year 0)
    current_principal_component = principal
    current_total_deposits_component = Decimal('0')
    current_interest_earned_component = Decimal('0')
    
    history.append({
        'year': 0,
        'balance': principal,
        'principal_component': current_principal_component,
        'total_deposits_component': current_total_deposits_component,
        'interest_earned_component': current_interest_earned_component
    })

    for year in range(1, int(years) + 1):
        # Calculate balance for the current year
        balance = calculate_future_value(principal, annual_rate, Decimal(year), periods_per_year, periodic_deposit, deposit_at_beginning)
        
        # Total deposits made over time
        total_deposits_component_current_year = periodic_deposit * Decimal(periods_per_year) * Decimal(year)

        # Interest is the total balance minus initial principal and total deposits
        interest_earned_component_current_year = balance - principal - total_deposits_component_current_year

        history.append({
            'year': year,
            'balance': balance,
            'principal_component': principal, # Initial principal remains constant
            'total_deposits_component': total_deposits_component_current_year,
            'interest_earned_component': interest_earned_component_current_year
        })
    
    return history

def calculate_final_balance_and_history(principal, annual_rate, years, periods_per_year, periodic_deposit, deposit_at_beginning):
    """
    Calculates final balance and generates data for a chart.
    """
    principal = Decimal(principal)
    periodic_deposit = Decimal(periodic_deposit)
    annual_rate = Decimal(annual_rate)

    if principal < 0: return {"error": "Initial Balance must be zero or positive."}
    if periodic_deposit < 0: return {"error": "Periodic Deposit must be zero or positive."}
    if annual_rate < 0: return {"error": "Annual Interest Rate must be zero or positive."}
    if years <= 0: return {"error": "Duration (Years) must be a positive integer."}
    if periods_per_year <= 0: return {"error": "Deposit Frequency must be at least once a year."}

    history = _generate_compound_history(principal, annual_rate, years, periods_per_year, periodic_deposit, deposit_at_beginning)
    final_result = history[-1]
    
    # Prepare data in a Chart.js-friendly format
    chart_data = {
        'labels': [h['year'] for h in history],
        'datasets': [
            {
                'label': 'Initial Principal',
                'data': [float(h['principal_component']) for h in history],
                'backgroundColor': 'rgba(59, 130, 246, 0.7)', # Blue
                'borderColor': 'rgba(59, 130, 246, 1)',
                'borderWidth': 1
            },
            {
                'label': 'Total Deposits',
                'data': [float(h['total_deposits_component']) for h in history],
                'backgroundColor': 'rgba(16, 185, 129, 0.7)', # Green
                'borderColor': 'rgba(16, 185, 129, 1)',
                'borderWidth': 1
            },
            {
                'label': 'Interest Earned',
                'data': [float(h['interest_earned_component']) for h in history],
                'backgroundColor': 'rgba(245, 158, 11, 0.7)', # Amber
                'borderColor': 'rgba(245, 158, 11, 1)',
                'borderWidth': 1
            }
        ]
    }

    return {
        "final_balance": final_result['balance'],
        "principal": principal,
        "total_deposits": final_result['total_deposits_component'],
        "interest_earned": final_result['interest_earned_component'],
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
    if goal_balance <= principal and periodic_deposit == 0:
        return {"note": "Your initial balance already meets or exceeds your goal, or you have no deposits to grow it."}

    low_years = Decimal('0')
    high_years = Decimal('200') # Max 200 years to prevent infinite loop

    # Check if goal is reachable at all with initial capital and no deposits/interest if applicable
    if annual_rate == 0 and periodic_deposit == 0:
        if principal >= goal_balance:
            return {"years": low_years, "calculated_field": "years", "chart_data": None} # Goal already met
        else:
            return {"error": "With zero interest and zero periodic deposits, goal is unreachable without more capital."}

    # Binary search for years
    for _ in range(100): # 100 iterations for precision
        mid_years = (low_years + high_years) / Decimal('2')
        if mid_years == low_years or mid_years == high_years: # Prevent infinite loop if values converge too slowly
            break
        
        fv = calculate_future_value(principal, annual_rate, mid_years, periods_per_year, periodic_deposit, deposit_at_beginning)
        
        if fv < goal_balance:
            low_years = mid_years
        else:
            high_years = mid_years
            
    final_years = high_years # High_years will be the first value to exceed goal
    
    if final_years > Decimal('199'): # If it hits max years, it might be unreachable
        return {"error": f"Goal of €{goal_balance:,.2f} unreachable within {int(high_years)} years with given inputs. Consider increasing deposit/initial balance/interest rate."}

    # Generate history for the chart based on the calculated years
    history = _generate_compound_history(principal, annual_rate, final_years, periods_per_year, periodic_deposit, deposit_at_beginning)
    
    chart_data = {
        'labels': [h['year'] for h in history],
        'datasets': [
            {
                'label': 'Initial Principal',
                'data': [float(h['principal_component']) for h in history],
                'backgroundColor': 'rgba(59, 130, 246, 0.7)', # Blue
                'borderColor': 'rgba(59, 130, 246, 1)',
                'borderWidth': 1
            },
            {
                'label': 'Total Deposits',
                'data': [float(h['total_deposits_component']) for h in history],
                'backgroundColor': 'rgba(16, 185, 129, 0.7)', # Green
                'borderColor': 'rgba(16, 185, 129, 1)',
                'borderWidth': 1
            },
            {
                'label': 'Interest Earned',
                'data': [float(h['interest_earned_component']) for h in history],
                'backgroundColor': 'rgba(245, 158, 11, 0.7)', # Amber
                'borderColor': 'rgba(245, 158, 11, 1)',
                'borderWidth': 1
            }
        ]
    }

    return {
        "years": final_years,
        "final_balance": calculate_future_value(principal, annual_rate, final_years, periods_per_year, periodic_deposit, deposit_at_beginning),
        "chart_data": chart_data,
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
        return {"note": f"Your initial principal (€{principal:,.2f}) already grows to €{fv_principal_only:,.2f}, which meets or exceeds your goal of €{goal_balance:,.2f} without any periodic deposits. Required deposit is €0.00."}

    # Remaining future value needed from deposits
    required_fv_from_deposits = goal_balance - fv_principal_only

    # Calculate PMT (periodic deposit)
    if rate_per_period > 0:
        denominator = ((Decimal('1') + rate_per_period) ** num_periods - Decimal('1')) / rate_per_period
        if deposit_at_beginning:
            denominator *= (Decimal('1') + rate_per_period)
        
        if denominator == 0: # Should not happen if rate_per_period > 0 and num_periods > 0
            return {"error": "Cannot calculate required periodic deposit due to mathematical impossibility (denominator is zero)."}
        
        required_deposit = required_fv_from_deposits / denominator
    else: # rate_per_period == 0
        required_deposit = required_fv_from_deposits / num_periods
    
    if required_deposit < 0:
        # This can happen if goal_balance is less than fv_principal_only, 
        # but was not caught by the fv_principal_only >= goal_balance check due to precision
        return {"note": f"Your initial principal already grows to €{fv_principal_only:,.2f}, which exceeds your goal of €{goal_balance:,.2f}. No periodic deposit is needed."}
        
    # Generate history for the chart based on the calculated periodic deposit
    history = _generate_compound_history(principal, annual_rate, years, periods_per_year, required_deposit, deposit_at_beginning)

    chart_data = {
        'labels': [h['year'] for h in history],
        'datasets': [
            {
                'label': 'Initial Principal',
                'data': [float(h['principal_component']) for h in history],
                'backgroundColor': 'rgba(59, 130, 246, 0.7)', # Blue
                'borderColor': 'rgba(59, 130, 246, 1)',
                'borderWidth': 1
            },
            {
                'label': 'Total Deposits',
                'data': [float(h['total_deposits_component']) for h in history],
                'backgroundColor': 'rgba(16, 185, 129, 0.7)', # Green
                'borderColor': 'rgba(16, 185, 129, 1)',
                'borderWidth': 1
            },
            {
                'label': 'Interest Earned',
                'data': [float(h['interest_earned_component']) for h in history],
                'backgroundColor': 'rgba(245, 158, 11, 0.7)', # Amber
                'borderColor': 'rgba(245, 158, 11, 1)',
                'borderWidth': 1
            }
        ]
    }
    
    return {
        "periodic_deposit": required_deposit,
        "final_balance": calculate_future_value(principal, annual_rate, years, periods_per_year, required_deposit, deposit_at_beginning),
        "chart_data": chart_data,
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
        return {"note": f"Your investment reaches €{fv_at_zero_rate:,.2f} with 0% interest, already meeting or exceeding your goal of €{goal_balance:,.2f}. Required interest rate is 0.00%."}

    low_rate = Decimal('0')
    high_rate = Decimal('1000') # Search up to 1000% annual rate

    # Binary search for annual_rate
    for _ in range(100): # 100 iterations for precision
        mid_rate = (low_rate + high_rate) / Decimal('2')
        if mid_rate == low_rate or mid_rate == high_rate: # Prevent infinite loop if values converge too slowly
            break

        fv = calculate_future_value(principal, mid_rate, years_dec, periods_per_year_dec, periodic_deposit, deposit_at_beginning)

        if fv < goal_balance:
            low_rate = mid_rate
        else:
            high_rate = mid_rate
            
    final_rate = high_rate # High_rate will be the first value to exceed goal
    
    if final_rate > Decimal('999'): # If it hits max rate, it might be unreachable
        return {"error": f"Goal of €{goal_balance:,.2f} unreachable with an annual interest rate up to {float(high_rate):.0f}%."}

    # Generate history for the chart based on the calculated interest rate
    history = _generate_compound_history(principal, final_rate, years, periods_per_year, periodic_deposit, deposit_at_beginning)

    chart_data = {
        'labels': [h['year'] for h in history],
        'datasets': [
            {
                'label': 'Initial Principal',
                'data': [float(h['principal_component']) for h in history],
                'backgroundColor': 'rgba(59, 130, 246, 0.7)', # Blue
                'borderColor': 'rgba(59, 130, 246, 1)',
                'borderWidth': 1
            },
            {
                'label': 'Total Deposits',
                'data': [float(h['total_deposits_component']) for h in history],
                'backgroundColor': 'rgba(16, 185, 129, 0.7)', # Green
                'borderColor': 'rgba(16, 185, 129, 1)',
                'borderWidth': 1
            },
            {
                'label': 'Interest Earned',
                'data': [float(h['interest_earned_component']) for h in history],
                'backgroundColor': 'rgba(245, 158, 11, 0.7)', # Amber
                'borderColor': 'rgba(245, 158, 11, 1)',
                'borderWidth': 1
            }
        ]
    }

    return {
        "interest_rate": final_rate,
        "final_balance": calculate_future_value(principal, final_rate, years, periods_per_year, periodic_deposit, deposit_at_beginning),
        "chart_data": chart_data,
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
    else:
        fv_deposits = periodic_deposit * num_periods

    # Future value needed from initial principal component
    required_fv_from_principal = goal_balance - fv_deposits

    if required_fv_from_principal <= 0:
        return {"note": f"Your periodic deposits (€{periodic_deposit:,.2f}) already grow to €{fv_deposits:,.2f}, which meets or exceeds your goal of €{goal_balance:,.2f}. No initial balance is needed."}

    # Calculate required initial principal (P)
    # FV_principal = P * (1 + r/n)^nt  => P = FV_principal / (1 + r/n)^nt
    compound_factor = (Decimal('1') + rate_per_period) ** num_periods
    if compound_factor == 0: # Should not happen with positive rate/periods
         return {"error": "Cannot calculate required initial balance due to mathematical impossibility (compound factor is zero)."}
         
    required_principal = required_fv_from_principal / compound_factor
    
    if required_principal < 0:
        return {"error": "Calculated initial principal is negative, which is not a valid financial scenario. Please check inputs, especially if your goal is too low relative to deposits."}

    # Generate history for the chart based on the calculated initial balance
    history = _generate_compound_history(required_principal, annual_rate, years, periods_per_year, periodic_deposit, deposit_at_beginning)
    
    chart_data = {
        'labels': [h['year'] for h in history],
        'datasets': [
            {
                'label': 'Initial Principal',
                'data': [float(h['principal_component']) for h in history],
                'backgroundColor': 'rgba(59, 130, 246, 0.7)', # Blue
                'borderColor': 'rgba(59, 130, 246, 1)',
                'borderWidth': 1
            },
            {
                'label': 'Total Deposits',
                'data': [float(h['total_deposits_component']) for h in history],
                'backgroundColor': 'rgba(16, 185, 129, 0.7)', # Green
                'borderColor': 'rgba(16, 185, 129, 1)',
                'borderWidth': 1
            },
            {
                'label': 'Interest Earned',
                'data': [float(h['interest_earned_component']) for h in history],
                'backgroundColor': 'rgba(245, 158, 11, 0.7)', # Amber
                'borderColor': 'rgba(245, 158, 11, 1)',
                'borderWidth': 1
            }
        ]
    }

    return {
        "initial_balance": required_principal,
        "final_balance": calculate_future_value(required_principal, annual_rate, years, periods_per_year, periodic_deposit, deposit_at_beginning),
        "chart_data": chart_data,
        "calculated_field": "initial_balance"
    }

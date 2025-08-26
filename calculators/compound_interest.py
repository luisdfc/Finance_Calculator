from decimal import Decimal

def calculate_future_value(principal, annual_rate, years, periods_per_year, periodic_deposit, deposit_at_beginning):
    """Calculates the future value of an investment with periodic deposits."""
    # Ensure all inputs are Decimal for precision
    principal = Decimal(principal)
    annual_rate = Decimal(annual_rate)
    periodic_deposit = Decimal(periodic_deposit)
    
    # Input validation moved to the main calculation function for consistency
    if not (principal >= 0 and annual_rate >= 0 and years >= 0 and periods_per_year >= 0 and periodic_deposit >= 0):
        return {"error": "All numeric inputs must be positive or zero."}
    
    # Handle the case where periods_per_year is zero to avoid division by zero
    if periods_per_year == 0:
        return principal + (periodic_deposit * years) # Simple sum if no compounding

    rate_per_period = (annual_rate / Decimal('100')) / Decimal(periods_per_year)
    num_periods = Decimal(years * periods_per_year)

    # Use Decimal throughout the calculation
    fv_principal = principal * ((Decimal('1') + rate_per_period) ** num_periods)

    if rate_per_period > 0:
        fv_deposits = periodic_deposit * (((Decimal('1') + rate_per_period) ** num_periods - Decimal('1')) / rate_per_period)
        if deposit_at_beginning:
            fv_deposits *= (Decimal('1') + rate_per_period)
    else:
        # If no interest, it's just the sum of deposits
        fv_deposits = periodic_deposit * num_periods
        
    return fv_principal + fv_deposits

def calculate_future_value_and_history(principal, annual_rate, years, periods_per_year, periodic_deposit, deposit_at_beginning):
    """
    Calculates final balance and generates data for a chart in a Chart.js-friendly format.
    """
    # Specific input validation for the web context, ensuring Decimal comparison
    principal_dec = Decimal(principal)
    periodic_deposit_dec = Decimal(periodic_deposit)
    annual_rate_dec = Decimal(annual_rate)

    if principal_dec < 0: return {"error": "Initial Balance must be zero or positive."}
    if periodic_deposit_dec < 0: return {"error": "Periodic Deposit must be zero or positive."}
    if annual_rate_dec < 0: return {"error": "Annual Interest Rate must be zero or positive."}
    if years <= 0: return {"error": "Duration (Years) must be a positive integer."}
    if periods_per_year <= 0: return {"error": "Deposit Frequency must be at least once a year."}

    history = []
    
    # Initialize values for the first year (year 0) using Decimal
    current_principal_component = principal_dec
    current_total_deposits_component = Decimal('0')
    current_interest_earned_component = Decimal('0')
    
    history.append({
        'year': 0,
        'balance': principal_dec,
        'principal_component': current_principal_component,
        'total_deposits_component': current_total_deposits_component,
        'interest_earned_component': current_interest_earned_component
    })

    for year in range(1, years + 1):
        # Calculate balance for the current year
        balance = calculate_future_value(principal_dec, annual_rate_dec, year, periods_per_year, periodic_deposit_dec, deposit_at_beginning)
        
        # Calculate components up to the current year
        total_contributions_so_far = principal_dec + (periodic_deposit_dec * periods_per_year * year)
        
        # The principal component remains the initial principal
        principal_component_current_year = principal_dec

        # Total deposits made over time
        total_deposits_component_current_year = periodic_deposit_dec * Decimal(periods_per_year) * Decimal(year)

        # Interest is the total balance minus initial principal and total deposits
        interest_earned_component_current_year = balance - principal_component_current_year - total_deposits_component_current_year

        history.append({
            'year': year,
            'balance': balance,
            'principal_component': principal_component_current_year,
            'total_deposits_component': total_deposits_component_current_year,
            'interest_earned_component': interest_earned_component_current_year
        })
    
    final_result = history[-1]

    # Prepare data in a Chart.js-friendly format
    chart_data = {
        'labels': [h['year'] for h in history],
        'datasets': [
            {
                'label': 'Initial Principal',
                'data': [h['principal_component'] for h in history],
                'backgroundColor': 'rgba(59, 130, 246, 0.7)', # Blue
                'borderColor': 'rgba(59, 130, 246, 1)',
                'borderWidth': 1
            },
            {
                'label': 'Total Deposits',
                'data': [h['total_deposits_component'] for h in history],
                'backgroundColor': 'rgba(16, 185, 129, 0.7)', # Green
                'borderColor': 'rgba(16, 185, 129, 1)',
                'borderWidth': 1
            },
            {
                'label': 'Interest Earned',
                'data': [h['interest_earned_component'] for h in history],
                'backgroundColor': 'rgba(245, 158, 11, 0.7)', # Amber
                'borderColor': 'rgba(245, 158, 11, 1)',
                'borderWidth': 1
            }
        ]
    }

    return {
        "final_balance": final_result['balance'],
        "principal": principal_dec, # Keep original principal for display
        "total_deposits": final_result['total_deposits_component'], # Total deposits at the end
        "interest_earned": final_result['interest_earned_component'], # Total interest at the end
        "chart_data": chart_data # Pass the structured data
    }
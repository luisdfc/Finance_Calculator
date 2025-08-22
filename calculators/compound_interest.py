import plotly.graph_objects as go

def calculate_future_value(principal, annual_rate, years, periods_per_year, periodic_deposit, deposit_at_beginning):
    """Calculates the future value of an investment with periodic deposits."""
    if periods_per_year == 0:
        return principal
    
    rate_per_period = (annual_rate / 100) / periods_per_year
    num_periods = years * periods_per_year

    fv_principal = principal * ((1 + rate_per_period) ** num_periods)

    if rate_per_period > 0:
        fv_deposits = periodic_deposit * (((1 + rate_per_period) ** num_periods - 1) / rate_per_period)
        if deposit_at_beginning:
            fv_deposits *= (1 + rate_per_period)
    else:
        fv_deposits = periodic_deposit * num_periods
        
    return fv_principal + fv_deposits

def calculate_future_value_and_history(principal, annual_rate, years, periods_per_year, periodic_deposit, deposit_at_beginning):
    """Calculates final balance and generates data for a plot."""
    history = []
    for year in range(years + 1):
        balance = calculate_future_value(principal, annual_rate, year, periods_per_year, periodic_deposit, deposit_at_beginning)
        total_deposits = periodic_deposit * periods_per_year * year
        interest = balance - principal - total_deposits
        history.append({
            'year': year,
            'balance': balance,
            'principal': principal,
            'total_deposits': total_deposits,
            'interest_earned': interest
        })
    
    final_result = history[-1]

    # Create a Plotly figure
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=[h['year'] for h in history],
        y=[h['principal'] for h in history],
        name='Balance Inicial'
    ))
    fig.add_trace(go.Bar(
        x=[h['year'] for h in history],
        y=[h['total_deposits'] for h in history],
        name='Aportaciones Totales'
    ))
    fig.add_trace(go.Bar(
        x=[h['year'] for h in history],
        y=[h['interest_earned'] for h in history],
        name='Intereses Generados'
    ))

    fig.update_layout(
        barmode='stack',
        title_text='Crecimiento de la Inversión a lo Largo del Tiempo'
    )
    
    # Get HTML for the plot
    plot_html = fig.to_html(full_html=False, include_plotlyjs=False, default_height='400px', config={'displayModeBar': False})

    return {
        "final_balance": final_result['balance'],
        "principal": final_result['principal'],
        "total_deposits": final_result['total_deposits'],
        "interest_earned": final_result['interest_earned'],
        "plot_html": plot_html
    }
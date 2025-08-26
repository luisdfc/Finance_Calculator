# calculators/capital_gains.py
from decimal import Decimal

def calculate_required_return(current_value, cost_basis, tax_rate):
    """
    Calculates the required return on a new investment to justify
    selling a current one and paying capital gains tax.
    """
    current_value = Decimal(current_value)
    cost_basis = Decimal(cost_basis)
    tax_rate = Decimal(tax_rate)

    if current_value <= 0:
        return {"error": "Current Investment Value must be a positive number."}
    if cost_basis <= 0:
        return {"error": "Original Cost Basis must be a positive number."}
    if not (Decimal('0') <= tax_rate < Decimal('1')):
        return {"error": "Capital Gains Tax Rate must be between 0 (0%) and 1 (100%)."}

    if current_value < cost_basis:
        return {
            "note": "The current value is less than the cost basis, resulting in a capital loss. There is no tax cost, so any new investment with a positive return is technically better."
        }

    capital_gain = current_value - cost_basis
    tax_cost = tax_rate * capital_gain
    post_tax_proceeds = current_value - tax_cost

    if post_tax_proceeds <= 0:
        return {"error": "Post-tax proceeds are zero or less. Cannot calculate a meaningful return because there's no capital left to reinvest after tax."}

    required_return = tax_cost / post_tax_proceeds
    return {
        "capital_gain": capital_gain,
        "tax_cost": tax_cost,
        "post_tax_proceeds": post_tax_proceeds,
        "required_return": required_return
    }

def generate_tax_rate_chart_data(current_value, cost_basis, max_tax_rate=Decimal('0.40')):
    """
    Generates data for a chart showing required return vs. tax rate.
    """
    if current_value <= 0 or cost_basis <= 0 or current_value < cost_basis:
        return None # Cannot generate meaningful chart data

    tax_rates = [Decimal(i) / Decimal('100') for i in range(0, int(max_tax_rate * 100) + 1, 2)] # From 0% to max_tax_rate, in 2% increments
    required_returns = []

    for rate in tax_rates:
        result = calculate_required_return(current_value, cost_basis, rate)
        if "error" not in result and "note" not in result:
            required_returns.append(result['required_return'])
        else:
            required_returns.append(Decimal('0')) # Or None, depending on desired chart behavior

    # Convert Decimals to floats for Chart.js
    chart_data = {
        'labels': [f"{float(r*100):.0f}%" for r in tax_rates],
        'datasets': [
            {
                'label': 'Required Return',
                'data': [float(rr) for rr in required_returns],
                'borderColor': 'rgba(79, 70, 229, 1)', # Indigo
                'backgroundColor': 'rgba(79, 70, 229, 0.2)',
                'fill': True,
                'tension': 0.4,
                'pointBackgroundColor': 'rgba(79, 70, 229, 1)'
            }
        ]
    }
    return chart_data
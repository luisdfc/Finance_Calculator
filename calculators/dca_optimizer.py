import math
from decimal import Decimal

def calculate_optimal_dca(total_capital, share_price, commission_fee, annualized_volatility, share_type='whole'):
    """
    Calculates the optimal number of trades and the price-drop trigger for a DCA strategy.
    """
    # Ensure all inputs are Decimal for precision
    total_capital = Decimal(total_capital)
    share_price = Decimal(share_price)
    commission_fee = Decimal(commission_fee)
    annualized_volatility = Decimal(annualized_volatility)

    if total_capital <= 0:
        return {"error": "Total Capital must be a positive number."}
    if share_price <= 0:
        return {"error": "Current Share Price must be a positive number."}
    if commission_fee < 0:
        return {"error": "Commission Fee per Trade cannot be negative."}
    if annualized_volatility < 0:
        return {"error": "Annualized Volatility cannot be negative."}

    # Constraint 1: Total commissions should not exceed 5% of total capital.
    if commission_fee > 0:
        n_commission_cap = (Decimal('0.05') * total_capital) / commission_fee
        n_commission_cap = math.floor(n_commission_cap)
    else:
        n_commission_cap = Decimal('inf') 

    # Constraint 2: Each trade must be viable.
    if share_type == 'whole':
        # For whole shares, each trade must be large enough to buy at least one share.
        if (share_price + commission_fee) > 0:
            n_viability_constraint = total_capital / (share_price + commission_fee)
            n_viability_constraint = math.floor(n_viability_constraint)
        else:
            n_viability_constraint = 0
    else: # Fractional shares
        # For fractional shares, each trade just needs to be larger than the commission.
        if commission_fee > 0:
            n_viability_constraint = total_capital / commission_fee
        else:
            # If no commission, this constraint is not a limiting factor for fractional shares
            n_viability_constraint = Decimal('inf')

    n_optimal = min(n_commission_cap, n_viability_constraint)

    if n_optimal <= 0:
        if share_type == 'whole':
            return {"error": f"Investment not feasible. You cannot afford one whole share (€{share_price:,.2f}) plus commission (€{commission_fee:,.2f}) with your capital."}
        else:
            return {"error": f"Investment not feasible. Your capital per trade would be less than the commission fee (€{commission_fee:,.2f})."}
    
    # This is the actionable amount of money to set aside for each trade.
    cash_per_trade = total_capital / Decimal(n_optimal)
    
    # Calculate total shares that can be bought after accounting for all commissions
    investable_capital = total_capital - (Decimal(n_optimal) * commission_fee)
    if investable_capital <= 0:
        return {"error": f"Investment not feasible. Total commissions (€{Decimal(n_optimal) * commission_fee:,.2f}) would exceed your total capital."}

    total_shares_bought = investable_capital / share_price
    if share_type == 'whole':
        total_shares_bought = Decimal(math.floor(total_shares_bought))

    if total_shares_bought <= 0:
        return {"error": "Investment not feasible. After commissions, there is not enough capital to buy any shares."}

    # Ensure annualized_volatility is handled for n_optimal > 0 case
    if n_optimal > 0:
        optimal_percentage_drop = annualized_volatility / Decimal(math.sqrt(n_optimal))
    else:
        optimal_percentage_drop = Decimal('0')

    return {
        "optimal_trades": int(n_optimal),
        "trigger_percentage": optimal_percentage_drop,
        "cash_per_trade": cash_per_trade,
        "total_shares_bought": total_shares_bought,
        "share_type": share_type
    }

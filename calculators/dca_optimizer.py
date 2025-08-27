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

    # Constraint 1: Total commissions should not exceed 5% of total capital.
    if commission_fee > 0:
        n_commission_cap = math.floor((Decimal('0.05') * total_capital) / commission_fee)
    else:
        n_commission_cap = float('inf') 

    # Determine the maximum possible number of trades to start our search from.
    if share_type == 'whole':
        if (share_price + commission_fee) > 0:
            max_possible_trades = math.floor(total_capital / (share_price + commission_fee))
        else:
            max_possible_trades = 0
    else: # Fractional shares
        if commission_fee > 0:
            max_possible_trades = n_commission_cap if n_commission_cap != float('inf') else 1000
        else:
            max_possible_trades = 1000

    n_optimal = 0
    # Iterate downwards to find the best number of trades
    for n in range(int(max_possible_trades), 0, -1):
        if n > n_commission_cap:
            continue

        cash_per_trade = total_capital / Decimal(n)
        investable_cash_per_trade = cash_per_trade - commission_fee

        if investable_cash_per_trade <= 0:
            continue

        if share_type == 'whole':
            if investable_cash_per_trade >= share_price:
                n_optimal = n
                break 
        else: # Fractional shares
            n_optimal = n
            break
            
    if n_optimal == 0:
        if share_type == 'whole':
            return {"error": f"Investment not feasible. You cannot afford one whole share (€{share_price:,.2f}) plus commission (€{commission_fee:,.2f}) with your capital."}
        else:
            return {"error": f"Investment not feasible. Your capital per trade would be less than the commission fee (€{commission_fee:,.2f})."}

    # --- Final Calculations based on n_optimal ---
    investable_capital = total_capital - (Decimal(n_optimal) * commission_fee)
    
    if investable_capital <= 0:
        return {"error": f"Investment not feasible. Total commissions (€{Decimal(n_optimal) * commission_fee:,.2f}) would exceed your total capital."}

    total_shares_bought = investable_capital / share_price

    if share_type == 'whole':
        total_shares_bought = Decimal(math.floor(total_shares_bought))
        if n_optimal > 0:
            total_shares_bought = (total_shares_bought // n_optimal) * n_optimal

    if total_shares_bought <= 0:
         return {"error": "Investment not feasible. After commissions, there is not enough capital to buy any shares."}

    # New calculations for clarity
    total_commissions = commission_fee * n_optimal
    cost_of_shares = total_shares_bought * share_price
    total_money_spent = cost_of_shares + total_commissions
    money_spent_per_trade = total_money_spent / n_optimal
    capital_leftover = total_capital - total_money_spent
    shares_per_trade = total_shares_bought / n_optimal if n_optimal > 0 else 0

    if annualized_volatility < 0:
        optimal_percentage_drop = Decimal('0')
    else:
        optimal_percentage_drop = annualized_volatility / Decimal(math.sqrt(n_optimal)) if n_optimal > 0 else Decimal('0')

    return {
        "optimal_trades": int(n_optimal),
        "trigger_percentage": optimal_percentage_drop,
        "total_shares_bought": total_shares_bought,
        "share_type": share_type,
        "total_money_spent": total_money_spent,
        "money_spent_per_trade": money_spent_per_trade,
        "total_commissions": total_commissions,
        "capital_leftover": capital_leftover,
        "shares_per_trade": shares_per_trade
    }
import math

def calculate_optimal_dca(total_capital, share_price, commission_fee, annualized_volatility):
    """
    Calculates the optimal number of trades and the price-drop trigger for a DCA strategy.
    """
    if share_price <= 0 or total_capital <= 0:
        return {"error": "Total capital and share price must be greater than zero."}

    # Constraint 1: Total commissions should not exceed 5% of total capital.
    if commission_fee > 0:
        n_commission_cap = math.floor((0.05 * total_capital) / commission_fee)
    else:
        n_commission_cap = math.floor(total_capital / share_price)

    # Constraint 2: Each trade must be large enough to buy at least one share.
    if (share_price + commission_fee) > 0:
        n_viability_constraint = math.floor(total_capital / (share_price + commission_fee))
    else:
        n_viability_constraint = 0

    n_optimal = min(n_commission_cap, n_viability_constraint)

    if n_optimal <= 0:
        return {"error": "Investment not feasible. The capital is too low to cover the share price and commission for even one trade."}

    optimal_percentage_drop = (annualized_volatility / math.sqrt(n_optimal)) if n_optimal > 0 else 0

    return {
        "optimal_trades": n_optimal,
        "trigger_percentage": optimal_percentage_drop,
        "capital_per_trade": total_capital / n_optimal
    }
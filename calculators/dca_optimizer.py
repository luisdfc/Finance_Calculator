"""Utility function for the Dollar-Cost Averaging (DCA) strategy optimizer."""

import math
from dataclasses import dataclass


@dataclass
class DCAResult:
    optimal_trades: int
    trigger_percentage: float
    capital_per_trade: float


class DCAError(ValueError):
    """Raised when the DCA strategy cannot be computed with given inputs."""


def calculate_optimal_dca(total_capital: float, share_price: float, commission_fee: float,
                           annualized_volatility: float) -> DCAResult:
    """Determine optimal trade count and price trigger for a DCA strategy."""
    if total_capital <= 0 or share_price <= 0 or commission_fee < 0 or annualized_volatility < 0:
        raise DCAError("Inputs must be positive numbers (commission can be 0).")

    if commission_fee > 0:
        n_commission_cap = math.floor((0.05 * total_capital) / commission_fee)
    else:
        n_commission_cap = math.floor(total_capital / share_price)

    if (share_price + commission_fee) > 0:
        n_viability_constraint = math.floor(total_capital / (share_price + commission_fee))
    else:
        n_viability_constraint = 0

    n_optimal = min(n_commission_cap, n_viability_constraint)
    if n_optimal <= 0:
        raise DCAError("Investment not feasible; capital too low for a single trade.")

    trigger_percentage = (annualized_volatility / math.sqrt(n_optimal)) if n_optimal > 0 else 0
    capital_per_trade = total_capital / n_optimal
    return DCAResult(n_optimal, trigger_percentage, capital_per_trade)

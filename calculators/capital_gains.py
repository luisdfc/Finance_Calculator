"""Utility functions for the Capital Gains Opportunity Cost Calculator."""

from dataclasses import dataclass


@dataclass
class CapitalGainsResult:
    capital_gain: float
    tax_cost: float
    post_tax_proceeds: float
    required_return: float


class CapitalGainsError(ValueError):
    """Raised when inputs are invalid for the capital gains calculation."""


def breakeven_return(current_value: float, cost_basis: float, tax_rate: float) -> CapitalGainsResult:
    """Calculate the breakeven return after paying capital gains tax.

    Args:
        current_value: Current market value of the investment.
        cost_basis: Original purchase price of the investment.
        tax_rate: Capital gains tax rate expressed as a decimal.

    Returns:
        CapitalGainsResult containing intermediate values and the required return.

    Raises:
        CapitalGainsError: If any of the inputs are invalid or the calculation cannot be performed.
    """
    if current_value <= 0 or cost_basis <= 0 or not (0 <= tax_rate < 1):
        raise CapitalGainsError("Values must be positive and tax rate between 0 and 1.")

    if current_value < cost_basis:
        raise CapitalGainsError("Current value is below cost basis; this results in a capital loss.")

    capital_gain = current_value - cost_basis
    tax_cost = tax_rate * capital_gain
    post_tax_proceeds = current_value - tax_cost

    if post_tax_proceeds <= 0:
        raise CapitalGainsError("Post-tax proceeds are zero or negative; cannot compute return.")

    required_return = tax_cost / post_tax_proceeds
    return CapitalGainsResult(capital_gain, tax_cost, post_tax_proceeds, required_return)

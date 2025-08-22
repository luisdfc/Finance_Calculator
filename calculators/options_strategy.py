"""Option strategy helper functions."""

from dataclasses import dataclass


@dataclass
class ExpectedMoveResult:
    expected_move: float
    expected_percentage: float
    lower_bound: float
    upper_bound: float


@dataclass
class SellVsExerciseResult:
    profit_from_selling: float
    profit_from_exercising: float
    extrinsic_value: float


class OptionsError(ValueError):
    """Raised when provided inputs are invalid for option strategy calculations."""


def expected_move(stock_price: float, call_price: float, put_price: float) -> ExpectedMoveResult:
    """Calculate the market's expected move using an ATM straddle."""
    if stock_price <= 0 or call_price < 0 or put_price < 0:
        raise OptionsError("Prices must be non-negative and stock price positive.")
    move = call_price + put_price
    percentage = move / stock_price
    lower = stock_price - move
    upper = stock_price + move
    return ExpectedMoveResult(move, percentage, lower, upper)


def sell_vs_exercise(stock_price: float, strike_price: float, option_premium: float) -> SellVsExerciseResult:
    """Compare profits from selling versus exercising an option."""
    if stock_price <= 0 or strike_price <= 0 or option_premium < 0:
        raise OptionsError("Prices must be positive and premium non-negative.")
    if stock_price <= strike_price:
        raise OptionsError("Stock price must exceed strike price for an in-the-money call option.")
    intrinsic_value = stock_price - strike_price
    profit_sell = option_premium
    profit_exercise = intrinsic_value
    extrinsic = option_premium - intrinsic_value
    return SellVsExerciseResult(profit_sell, profit_exercise, extrinsic)

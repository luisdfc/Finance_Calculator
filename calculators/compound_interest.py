"""Compound interest calculation utilities."""

from __future__ import annotations

import base64
from dataclasses import dataclass
from io import BytesIO
from typing import List

import matplotlib.pyplot as plt
import numpy as np


@dataclass
class HistoryEntry:
    year: int
    balance: float
    principal: float
    total_deposits: float
    interest_earned: float


def future_value(principal: float, annual_rate: float, years: int, periods_per_year: int,
                 periodic_deposit: float, deposit_at_beginning: bool) -> tuple[float, List[HistoryEntry]]:
    """Calculate final balance and yearly history for an investment."""
    rate_per_period = (annual_rate / 100) / periods_per_year
    history: List[HistoryEntry] = []

    for year in range(years + 1):
        num_periods = year * periods_per_year
        fv_principal = principal * ((1 + rate_per_period) ** num_periods)
        if rate_per_period:
            fv_deposits = periodic_deposit * (((1 + rate_per_period) ** num_periods - 1) / rate_per_period)
            if deposit_at_beginning:
                fv_deposits *= (1 + rate_per_period)
        else:
            fv_deposits = periodic_deposit * num_periods
        balance = fv_principal + fv_deposits
        total_deposits = periodic_deposit * num_periods
        interest = balance - principal - total_deposits
        history.append(HistoryEntry(year, balance, principal, total_deposits, interest))
    final_balance = history[-1].balance
    return final_balance, history


def years_to_goal(principal: float, annual_rate: float, periods_per_year: int,
                  periodic_deposit: float, deposit_at_beginning: bool, goal: float,
                  max_years: int = 1000) -> tuple[int, List[HistoryEntry]]:
    """Return number of years required to reach a savings goal."""
    year = 0
    history: List[HistoryEntry] = []
    while year <= max_years:
        balance, hist = future_value(principal, annual_rate, year, periods_per_year,
                                     periodic_deposit, deposit_at_beginning)
        history = hist
        if balance >= goal:
            return year, history
        year += 1
    raise ValueError("Goal not reached within max_years")


def required_rate(principal: float, years: int, periods_per_year: int,
                  periodic_deposit: float, deposit_at_beginning: bool, goal: float,
                  tolerance: float = 0.0001) -> float:
    """Return annual rate needed to reach goal in given time."""
    low, high = 0.0, 100.0
    rate_val = None
    for _ in range(100):
        mid = (low + high) / 2
        balance, _ = future_value(principal, mid, years, periods_per_year,
                                  periodic_deposit, deposit_at_beginning)
        if abs(balance - goal) < tolerance:
            rate_val = mid
            break
        if balance < goal:
            low = mid
        else:
            high = mid
    if rate_val is None:
        rate_val = (low + high) / 2
    return rate_val


def required_deposit(principal: float, annual_rate: float, years: int, periods_per_year: int,
                     deposit_at_beginning: bool, goal: float) -> float:
    """Return periodic deposit required to reach a goal."""
    rate_per_period = (annual_rate / 100) / periods_per_year
    num_periods = years * periods_per_year
    fv_principal = principal * ((1 + rate_per_period) ** num_periods)
    required_fv = goal - fv_principal
    if required_fv <= 0:
        return 0.0
    if rate_per_period:
        denominator = (((1 + rate_per_period) ** num_periods - 1) / rate_per_period)
        if deposit_at_beginning:
            denominator *= (1 + rate_per_period)
        if denominator == 0:
            return 0.0
        return required_fv / denominator
    return required_fv / num_periods


def plot_history(history: List[HistoryEntry]) -> str:
    """Return a base64-encoded PNG of the investment growth history."""
    years = [h.year for h in history]
    principal = [h.principal for h in history]
    deposits = [h.total_deposits for h in history]
    interest = [h.interest_earned for h in history]

    principal_arr = np.array(principal)
    deposits_arr = np.array(deposits)
    interest_arr = np.array(interest)

    plt.style.use('seaborn-v0_8-darkgrid')
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(years, principal_arr, label='Initial Balance', color='#003f5c')
    ax.bar(years, deposits_arr, bottom=principal_arr, label='Total Contributions', color='#7a5195')
    ax.bar(years, interest_arr, bottom=principal_arr + deposits_arr, label='Interest', color='#ffa600')
    ax.set_xlabel('Years')
    ax.set_ylabel('Balance')
    ax.legend()
    buf = BytesIO()
    plt.tight_layout()
    fig.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.getvalue()).decode('utf-8')

import math

def calculate_optimal_dca(total_capital, share_price, commission_fee, annualized_volatility):
    """
    Calculates the optimal number of trades and the price-drop trigger for a DCA strategy.

    Args:
        total_capital (float): The total amount of money to invest.
        share_price (float): The current price of a single share.
        commission_fee (float): The flat commission fee per trade.
        annualized_volatility (float): The stock's annualized volatility (e.g., 0.60 for 60%).

    Returns:
        dict: A dictionary containing the optimal number of trades and the trigger percentage,
              or an error message if the calculation is not possible.
    """
    # --- 1. Calculate the Optimal Number of Trades (n) ---

    # Constraint 1: Total commissions should not exceed 5% of total capital.
    # n * commission_fee <= 0.05 * total_capital
    if commission_fee > 0:
        n_commission_cap = math.floor((0.05 * total_capital) / commission_fee)
    else:
        # If there are no commissions, this constraint is irrelevant.
        # We can set a high number, but it's better to rely on the viability constraint.
        # For simplicity, we'll calculate the max possible shares as a practical limit.
        n_commission_cap = math.floor(total_capital / share_price)


    # Constraint 2: Each trade must be large enough to buy at least one share.
    # C >= n * (P + F)
    if (share_price + commission_fee) > 0:
        n_viability_constraint = math.floor(total_capital / (share_price + commission_fee))
    else:
        n_viability_constraint = 0

    # The optimal number of trades is the minimum of the two constraints.
    n_optimal = min(n_commission_cap, n_viability_constraint)

    # Handle cases where an investment isn't feasible.
    if n_optimal <= 0:
        return {"error": "Investment not feasible. The capital is too low to cover the share price and commission for even one trade."}

    # --- 2. Calculate the Price-Based Trigger (Δ%) ---

    # Δ% = annualized_volatility / sqrt(n_optimal)
    # Ensure n_optimal is not zero to avoid division errors, though the check above should handle it.
    optimal_percentage_drop = (annualized_volatility / math.sqrt(n_optimal)) if n_optimal > 0 else 0

    return {
        "optimal_trades": n_optimal,
        "trigger_percentage": optimal_percentage_drop,
        "capital_per_trade": total_capital / n_optimal
    }

def main():
    """
    Main function to get user input and display the DCA strategy.
    """
    print("--- DCA Strategy Optimizer ---")
    print("This tool calculates the optimal number of trades and the price-drop trigger for your DCA strategy.")
    print("-" * 30)

    try:
        # Get user inputs
        capital = float(input("Enter your total capital to invest (e.g., 900): "))
        price = float(input("Enter the current share price (e.g., 3): "))
        fee = float(input("Enter the commission fee per trade (e.g., 5): "))
        volatility = float(input("Enter the stock's annualized volatility (e.g., 0.60 for 60%): "))

        if capital <= 0 or price <= 0 or fee < 0 or volatility < 0:
            print("\nError: All inputs must be positive numbers (commission can be 0).")
            return

        # Calculate the strategy
        strategy = calculate_optimal_dca(capital, price, fee, volatility)

        # Display the results
        print("\n--- Your Optimized DCA Strategy ---")
        if "error" in strategy:
            print(f"Error: {strategy['error']}")
        else:
            n_opt = strategy['optimal_trades']
            trigger_pct = strategy['trigger_percentage']
            cap_per_trade = strategy['capital_per_trade']
            
            print(f"Optimal Number of Trades: {n_opt}")
            print(f"Ideal Price-Drop Trigger: {trigger_pct:.2%}")
            print("-" * 30)
            print("\n--- How to Implement This Strategy ---")
            print(f"1. Divide your capital into {n_opt} parts of €{cap_per_trade:.2f} each.")
            print(f"2. Make your first purchase now at the current price.")
            print(f"3. For subsequent purchases, buy every time the stock drops by {trigger_pct:.2%} from your last purchase price.")

            # Example simulation
            print("\n--- Example Scenario ---")
            first_purchase_shares = math.floor((cap_per_trade - fee) / price)
            print(f"-> Your first purchase of ~€{cap_per_trade:.2f} would get you {first_purchase_shares} shares at ~€{price:.2f}.")
            
            next_price_target = price * (1 - trigger_pct)
            print(f"-> You would then set an alert to buy again when the price hits €{next_price_target:.2f}.")
            
            next_purchase_shares = math.floor((cap_per_trade - fee) / next_price_target)
            print(f"-> At that price, your next purchase would get you {next_purchase_shares} shares, maximizing the benefit of the dip.")

    except ValueError:
        print("\nError: Invalid input. Please enter valid numbers.")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")

if __name__ == "__main__":
    main()

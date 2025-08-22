import math

def calculate_expected_move():
    """
    Calculates the market's expected price move based on the ATM straddle cost.
    """
    print("\n--- Market's Expected Move Calculator ---")
    print("This calculates the expected stock price swing based on option prices.")
    
    try:
        stock_price = float(input("Enter the current stock price (e.g., 150): "))
        call_price = float(input(f"Enter the price of the ATM call option (strike price ~${stock_price}): "))
        put_price = float(input(f"Enter the price of the ATM put option (strike price ~${stock_price}): "))

        if stock_price <= 0 or call_price < 0 or put_price < 0:
            print("\nError: Prices must be positive numbers.")
            return

        # The expected move is the sum of the ATM call and put prices (the straddle cost).
        expected_move = call_price + put_price
        expected_percentage = (expected_move / stock_price)

        upper_bound = stock_price + expected_move
        lower_bound = stock_price - expected_move

        print("\n--- Calculation Results ---")
        print(f"Market's Expected Move: ${expected_move:.2f} (up or down)")
        print(f"Expected Move Percentage: {expected_percentage:.2%}")
        print(f"This implies a trading range between ${lower_bound:.2f} and ${upper_bound:.2f}.")
        print("\nFor a long call to be profitable, the stock must rise significantly MORE than this expected move.")

    except ValueError:
        print("\nError: Invalid input. Please enter valid numbers.")

def compare_sell_vs_exercise():
    """
    Compares the profit from selling an in-the-money option vs. exercising it.
    """
    print("\n--- Sell vs. Exercise Calculator ---")
    print("This shows why selling an option is almost always more profitable.")

    try:
        stock_price = float(input("Enter the current stock price (e.g., 165): "))
        strike_price = float(input("Enter the option's strike price (e.g., 155): "))
        option_premium = float(input("Enter the current premium (market price) of the option (e.g., 10.50): "))

        if stock_price <= 0 or strike_price <= 0 or option_premium < 0:
            print("\nError: Prices must be positive numbers.")
            return
        
        if stock_price <= strike_price:
            print("\nNote: This calculation is for an in-the-money call option (stock price > strike price).")
            return

        # --- Calculate Profits ---
        # 1. Profit from SELLING the option
        # Profit is simply the premium received per share.
        profit_from_selling = option_premium

        # 2. Profit from EXERCISING the option
        # This captures only the intrinsic value.
        intrinsic_value = stock_price - strike_price
        profit_from_exercising = intrinsic_value

        # 3. Calculate the Extrinsic Value
        # This is the extra money you get by selling.
        extrinsic_value = option_premium - intrinsic_value

        print("\n--- Comparison Results (per share) ---")
        print(f"Profit from SELLING the option: ${profit_from_selling:.2f}")
        print(f"Profit from EXERCISING the option: ${profit_from_exercising:.2f}")
        print("-" * 30)
        print(f"By selling, you gain an extra ${extrinsic_value:.2f} per share.")
        print("This extra amount is the remaining 'Extrinsic Value' (time value + volatility premium) that you forfeit when you exercise.")

    except ValueError:
        print("\nError: Invalid input. Please enter valid numbers.")


def main():
    """
    Main function to provide a menu for the user.
    """
    while True:
        print("\n--- Options Strategy Calculator Menu ---")
        print("1. Calculate the Market's Expected Move")
        print("2. Compare Selling vs. Exercising an Option")
        print("3. Exit")
        
        choice = input("Please choose an option (1, 2, or 3): ")

        if choice == '1':
            calculate_expected_move()
        elif choice == '2':
            compare_sell_vs_exercise()
        elif choice == '3':
            print("Exiting the program. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main()
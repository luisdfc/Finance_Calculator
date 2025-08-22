import math

def calculate_required_return():
    """
    Calculates the required return on a new investment to justify
    selling a current one and paying capital gains tax.
    """
    print("\n--- Capital Gains Opportunity Cost Calculator ---")
    print("This tool determines the minimum return a new investment needs to beat your current one after taxes.")
    
    try:
        # Get user inputs
        current_value = float(input("Enter the current value of your investment (V): "))
        cost_basis = float(input("Enter the original cost basis (C): "))
        tax_rate = float(input("Enter your capital gains tax rate as a decimal (e.g., 0.19 for 19%): "))

        # --- Input Validation ---
        if current_value <= 0 or cost_basis <= 0 or tax_rate < 0 or tax_rate >= 1:
            print("\nError: Values must be positive. Tax rate must be between 0 and 1.")
            return

        if current_value < cost_basis:
            print("\nNote: The current value is less than the cost basis, resulting in a capital loss.")
            print("There is no tax cost, so any new investment with a positive return is technically better.")
            return

        # --- Calculations ---
        # 1. Calculate the capital gain
        capital_gain = current_value - cost_basis

        # 2. Calculate the tax cost
        tax_cost = tax_rate * capital_gain

        # 3. Calculate the post-tax proceeds (the capital you can reinvest)
        post_tax_proceeds = current_value - tax_cost

        # 4. Calculate the required return on the new investment
        # This is the return needed to cover the tax cost with the new, smaller capital base.
        if post_tax_proceeds <= 0:
             print("\nError: Post-tax proceeds are zero or less. Cannot calculate a meaningful return.")
             return
        
        required_return = tax_cost / post_tax_proceeds

        # --- Display Results ---
        print("\n--- Analysis Results ---")
        print(f"Capital Gain: ${capital_gain:,.2f}")
        print(f"Tax Due Upon Selling (Tax Cost): ${tax_cost:,.2f}")
        print(f"Capital Available for Reinvestment (Post-Tax Proceeds): ${post_tax_proceeds:,.2f}")
        print("-" * 30)
        print(f"Required Breakeven Return on New Investment: {required_return:.2%}")
        print("\nConclusion:")
        print(f"A new investment opportunity must return AT LEAST {required_return:.2%} to be financially better")
        print("than simply holding your current asset. This percentage is the 'cost' of your tax bill.")


    except ValueError:
        print("\nError: Invalid input. Please enter valid numbers.")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")


def main():
    """
    Main function to run the calculator.
    """
    calculate_required_return()


if __name__ == "__main__":
    main()
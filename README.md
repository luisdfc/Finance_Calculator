# Financial Calculators for Investors
This repository contains a collection of Python-based command-line tools designed to help investors make more informed and optimized decisions. Each calculator addresses a specific financial question, from opportunity cost to advanced options strategies.

## Calculators
1. Capital Gains Opportunity Cost Calculator (Capital Gains Opportunity Cost Calculator.py)
This tool calculates the minimum return a new investment must generate to be more profitable than holding onto your current investment after accounting for capital gains taxes. It helps you answer the question: "Is it worth selling this asset to invest in something else?"

### Inputs Required:
Current Investment Value: The total current market value of your asset.

Original Cost Basis: The price you originally paid for the asset.

Capital Gains Tax Rate: Your applicable tax rate on the profit, entered as a decimal (e.g., 0.19 for 19%).

The script will output the breakeven return percentage required from a new investment to justify selling the current one.

### 2. DCA Strategy Optimizer (DCA Strategy Optimizer.py)
This script determines your optimal Dollar-Cost Averaging (DCA) strategy by balancing the benefits of averaging your cost basis against the impact of commission fees. It calculates both the ideal number of trades to make and the specific price drop percentage to use as a buying trigger.

Inputs Required:
Total Capital: The total amount of money you plan to invest.

Current Share Price: The current market price of one share.

Commission Fee: The flat fee your broker charges for each trade.

Annualized Volatility: A measure of the stock's price swings over a year. This should be entered as a decimal (e.g., 0.60 for 60%).

The script will output a personalized DCA plan, including the number of purchases to make and the price-drop percentage that should trigger each purchase.

### 3. Options Strategy Calculator (Options Strategy Calculator.py)
This tool provides two key calculations for options traders:

Market's Expected Move Calculator: Based on the price of an at-the-money (ATM) straddle, this tool calculates the price swing (up or down) that the market is anticipating for a stock. This is especially useful before an earnings report.

Sell vs. Exercise Calculator: This tool demonstrates the financial difference between selling a call option to close your position versus exercising it to buy the shares, highlighting the importance of extrinsic value.

You will run the script and choose which calculation you want to perform, then provide the required inputs like stock and option prices.

### 4. Compound Interest Calculator (Compound Interest Calculator.py)
This is an interactive tool for planning your long-term investments. It allows you to explore different financial scenarios based on the principle of compound interest and generates a graph to visualize the growth.

Main Features:
Calculate Final Balance: Project the future value of your investment.

Calculate Time Required: Determine how many years it will take to reach a specific savings goal.

Calculate Required Interest Rate: Find the annual return needed to reach your goal in a set time.

Calculate Periodic Contribution: Determine the regular deposit amount needed to reach your financial goal.

Inputs You May Need:
Initial Balance (€): The amount of money you start with.

Periodic Deposit (€): The amount you plan to add regularly.

Deposit Frequency: How often you will make contributions (annually, monthly, etc.).

Deposit Time: Whether the contribution is made at the beginning or end of each period.

Duration (Years): How many years you will maintain the investment.

Annual Interest Rate (%): The expected annual return on your investment (e.g., 7 for 7%).

Savings Goal (€): The amount of money you want to reach.
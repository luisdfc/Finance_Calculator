# 📊 FinCalc: Web-Based Financial Calculators for Investors

[![Python](https://img.shields.io/badge/python-3.x-blue.svg)](https://www.python.org/)  
[![Flask](https://img.shields.io/badge/flask-2.x-green.svg)](https://flask.palletsprojects.com/)  
[![License](https://img.shields.io/badge/license-MIT-lightgrey.svg)](LICENSE)

**FinCalc** is a modern, easy-to-use web application that provides a suite of powerful financial calculators. Designed for investors who want to make informed, data-driven decisions, FinCalc simplifies complex financial questions with a clean and intuitive interface.

---

## ✨ Features

This application includes four key calculators, each with unique functionalities:

### 1. 📈 Compound Interest Calculator
A versatile tool that not only projects the future value of your investments but can also solve for any missing variable. You can calculate:
- **Final Balance**: See how your investment will grow over time.
- **Time to Goal**: Determine how long it will take to reach a specific financial target.
- **Required Periodic Deposit**: Find out how much you need to save regularly to meet your goals.
- **Required Interest Rate**: Calculate the annual return needed to reach your target.
- **Required Initial Balance**: Determine the starting principal needed to achieve a future sum.

---

### 2. 💰 DCA Strategy Optimizer
An advanced tool to find your optimal **Dollar-Cost Averaging (DCA)** strategy. This calculator helps you balance commission costs by allowing you to set a custom **commission cap** (e.g., max 5% of capital for fees). It then determines the ideal number of trades and a price-drop percentage—based on the asset's volatility—that should trigger your next investment. The tool fully supports both **whole** and **fractional** share strategies, ensuring the plan is perfectly executable.

---

### 3. 🔄 Capital Gains Opportunity Cost
Decide if it’s worth selling an asset to reinvest elsewhere by calculating the **breakeven return** required on a new investment to make up for the taxes you'll pay on the sale of the first one.

---

### 4. ⚖️ Options Strategy Calculator
A dual-functionality tool for options traders:
- **Market's Expected Move**: Estimate the potential price swing of a stock based on the prices of its at-the-money options.
- **Sell vs. Exercise**: Compare the financial outcomes of selling your option versus exercising it to help you maximize your profit.

---

## 📸 Screenshots

Here's a look at the FinCalc interface:

**Main Page**
![Main Page](screenshots/Main_page.png)

**Compound Interest Calculator**
![Compound Interest Calculator](screenshots/Compound_Interest_Calculator.png)

**DCA Strategy Optimizer**
![DCA Strategy Optimizer](screenshots/DCA_Strategy_Optimizer.png)

**Capital Gains Opportunity Cost Calculator**
![Capital Gains Opportunity Cost Calculator](screenshots/Capital_Gains_Opportunity_Cost.png)

**Options Strategy Calculator**
![Options Strategy Calculator](screenshots/Options_Strategy_Calculator.png)

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.x installed  

### 2. Installation
Clone the repository:

```bash
git clone <repository-url>
cd <repository-folder>

```
Install the required Python packages using pip:
```bash
pip install -r requirements.txt
```

### 3. Running the Application
Once the dependencies are installed, you can start the Flask web server:

```bash
python app.py
```
The application will be running at:

http://127.0.0.1:5000

Open this URL in your web browser to start using the calculators.

## 🤝 Contributing

Contributions are welcome!
1. Fork the repo
2. Create a feature branch (git checkout -b feature-name)
3. Commit changes (git commit -m "Add feature")
4. Push and open a Pull Request

## 📜 License

This project is licensed under the MIT License.

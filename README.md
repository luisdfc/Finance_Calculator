# 📊 FinCalc: Web-Based Financial Calculators for Investors

[![Python](https://img.shields.io/badge/python-3.x-blue.svg)](https://www.python.org/)  
[![Flask](https://img.shields.io/badge/flask-2.x-green.svg)](https://flask.palletsprojects.com/)  
[![License](https://img.shields.io/badge/license-MIT-lightgrey.svg)](LICENSE)

**FinCalc** is a modern, easy-to-use web application that provides a suite of powerful financial calculators.  
Designed for investors who want to make informed, data-driven decisions, FinCalc simplifies complex financial questions with a clean and intuitive interface.

---

## ✨ Features

This application includes four key calculators:

### 1. 📈 Compound Interest Calculator
Project the future value of your investments and visualize growth with the power of compounding.  

Formula:  

\[
FV = P \times \left(1 + \frac{r}{n}\right)^{n \times t}
\]

Where:
- \(FV\): Future Value  
- \(P\): Principal amount  
- \(r\): Annual interest rate  
- \(n\): Compounding periods per year  
- \(t\): Time in years  

---

### 2. 💰 DCA Strategy Optimizer
Find your optimal **Dollar-Cost Averaging (DCA)** strategy.  
Balances commission costs against the benefits of averaging into a position.

---

### 3. 🔄 Capital Gains Opportunity Cost
Decide if it’s worth selling an asset to reinvest elsewhere by calculating the **breakeven return** required.  

\[
r_{new} \geq \frac{(FV_{current} - Tax)}{P_{new}}
\]

Where:
- \(r_{new}\): Required return of the new investment  
- \(FV_{current}\): Future value if you keep the current asset  
- \(Tax\): Capital gains tax liability  
- \(P_{new}\): Amount invested in the new opportunity  

---

### 4. ⚖️ Options Strategy Calculator

#### a) Market's Expected Move
Estimate price swings before events (e.g., earnings reports).  

\[
\text{Expected Move} \approx \frac{C_{ATM} + P_{ATM}}{S} \times 100
\]

Where:
- \(C_{ATM}\): ATM call price  
- \(P_{ATM}\): ATM put price  
- \(S\): Current stock price  

#### b) Sell vs. Exercise
Compare outcomes of selling vs. exercising an option.  

\[
\text{Option Price} = \text{Intrinsic Value} + \text{Extrinsic Value}
\]

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

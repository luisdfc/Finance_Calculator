from flask import Flask, render_template, request

from calculators.capital_gains import breakeven_return, CapitalGainsError
from calculators.dca_optimizer import calculate_optimal_dca, DCAError
from calculators.options_strategy import expected_move, sell_vs_exercise, OptionsError
from calculators.compound_interest import (
    future_value,
    years_to_goal,
    required_rate,
    required_deposit,
    plot_history,
)

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/capital-gains", methods=["GET", "POST"])
def capital_gains_view():
    result = None
    if request.method == "POST":
        try:
            cv = float(request.form["current_value"])
            cb = float(request.form["cost_basis"])
            tr = float(request.form["tax_rate"])
            res = breakeven_return(cv, cb, tr)
            result = res.__dict__
        except (ValueError, CapitalGainsError) as e:
            result = {"error": str(e)}
    return render_template("capital_gains.html", result=result)


@app.route("/dca", methods=["GET", "POST"])
def dca_view():
    result = None
    if request.method == "POST":
        try:
            capital = float(request.form["capital"])
            price = float(request.form["price"])
            fee = float(request.form["fee"])
            vol = float(request.form["volatility"])
            res = calculate_optimal_dca(capital, price, fee, vol)
            result = res.__dict__
        except (ValueError, DCAError) as e:
            result = {"error": str(e)}
    return render_template("dca.html", result=result)


@app.route("/options", methods=["GET", "POST"])
def options_view():
    result = None
    if request.method == "POST":
        calc_type = request.form.get("calc_type")
        try:
            if calc_type == "move":
                stock = float(request.form.get("stock_price", 0))
                call = float(request.form.get("call_price", 0))
                put = float(request.form.get("put_price", 0))
                res = expected_move(stock, call, put)
                result = {**res.__dict__, "type": "move"}
            else:
                stock = float(request.form.get("stock_price_sell", 0))
                strike = float(request.form.get("strike_price", 0))
                premium = float(request.form.get("option_premium", 0))
                res = sell_vs_exercise(stock, strike, premium)
                result = {**res.__dict__, "type": "sell"}
        except (ValueError, OptionsError) as e:
            result = {"error": str(e)}
    return render_template("options.html", result=result)


@app.route("/compound", methods=["GET", "POST"])
def compound_view():
    result = None
    if request.method == "POST":
        calc_type = request.form.get("calc_type")
        try:
            principal = float(request.form.get("principal", 0) or 0)
            deposit = float(request.form.get("deposit", 0) or 0)
            freq = int(request.form.get("frequency", 1) or 1)
            begin = bool(request.form.get("begin"))
            rate = float(request.form.get("rate", 0) or 0)
            years = float(request.form.get("years", 0) or 0)
            goal = float(request.form.get("goal", 0) or 0)
            if calc_type == "balance":
                balance, history = future_value(principal, rate, int(years), freq, deposit, begin)
                image = plot_history(history) if history else None
                result = {"type": "balance", "balance": balance, "image": image}
            elif calc_type == "time":
                y, _ = years_to_goal(principal, rate, freq, deposit, begin, goal)
                result = {"type": "time", "years": y}
            elif calc_type == "rate":
                r = required_rate(principal, int(years), freq, deposit, begin, goal)
                result = {"type": "rate", "rate": r}
            elif calc_type == "deposit":
                d = required_deposit(principal, rate, int(years), freq, begin, goal)
                result = {"type": "deposit", "deposit": d}
        except ValueError as e:
            result = {"error": str(e)}
    return render_template("compound.html", result=result)


if __name__ == "__main__":
    app.run(debug=True)

# app.py (UPDATED)

from flask import Flask, render_template, request
from calculators.web_calculators import (
    CompoundInterestWebCalculator,
    DCAOptimizerWebCalculator,
    CapitalGainsWebCalculator,
    OptionsStrategyWebCalculator
)

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/compound', methods=['GET', 'POST'])
def compound():
    calculator = CompoundInterestWebCalculator()
    result = None
    form_data = {}

    if request.method == 'POST':
        processed_data, form_data, input_error = calculator.process_form_data(request.form)
        if input_error:
            result = input_error # Use the specific error from process_form_data
        else:
            result = calculator.calculate(processed_data)
    else:
        form_data = calculator.get_default_form_data()

    return render_template('compound.html', result=result, form_data=form_data)

@app.route('/dca', methods=['GET', 'POST'])
def dca():
    calculator = DCAOptimizerWebCalculator()
    result = None
    form_data = {}

    if request.method == 'POST':
        processed_data, form_data, input_error = calculator.process_form_data(request.form)
        if input_error:
            result = input_error
        else:
            result = calculator.calculate(processed_data)
    else:
        form_data = calculator.get_default_form_data()

    return render_template('dca.html', result=result, form_data=form_data)

@app.route('/capital_gains', methods=['GET', 'POST'])
def capital_gains_calc():
    calculator = CapitalGainsWebCalculator()
    result = None
    form_data = {}

    if request.method == 'POST':
        processed_data, form_data, input_error = calculator.process_form_data(request.form)
        if input_error:
            result = input_error
        else:
            result = calculator.calculate(processed_data)
    else:
        form_data = calculator.get_default_form_data()

    return render_template('capital_gains.html', result=result, form_data=form_data)

@app.route('/options', methods=['GET', 'POST'])
def options():
    calculator = OptionsStrategyWebCalculator()
    result = None
    form_data = {}

    if request.method == 'POST':
        processed_data, form_data, input_error = calculator.process_form_data(request.form)
        if input_error:
            result = input_error
        else:
            result = calculator.calculate(processed_data)
    else:
        form_data = calculator.get_default_form_data()
        
    return render_template('options.html', result=result, form_data=form_data)

if __name__ == '__main__':
    app.run(debug=True)

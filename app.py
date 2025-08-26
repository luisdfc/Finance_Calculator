# app.py

from flask import Flask, render_template, request
from calculators.web_calculators import (
    CompoundInterestWebCalculator,
    DCAOptimizerWebCalculator, # Assuming these exist or will be added
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
        # process_form_data returns processed_data, raw_form_data (for re-populating form), and any input_error
        processed_data, form_data, input_error = calculator.process_form_data(request.form)
        if input_error:
            result = input_error # Display the specific input error
        else:
            # Pass the processed_data to the calculate method
            result = calculator.calculate(processed_data)
            # Merge form_data from processing with the result's calculated values for display
            if result and 'calculated_field' in result:
                # Update the specific input field in form_data with the calculated value
                # This ensures the calculated value appears in the input field when rendered
                if result['calculated_field'] == 'final_balance':
                    form_data['final_balance'] = compound_interest.round_decimal(result['final_balance'], 2)
                elif result['calculated_field'] == 'years':
                    form_data['duration_years'] = compound_interest.round_decimal(result['years'], 2)
                elif result['calculated_field'] == 'periodic_deposit':
                    form_data['periodic_deposit'] = compound_interest.round_decimal(result['periodic_deposit'], 2)
                elif result['calculated_field'] == 'interest_rate':
                    form_data['annual_interest_rate'] = compound_interest.round_decimal(result['interest_rate'], 2)
                elif result['calculated_field'] == 'initial_balance':
                    form_data['initial_balance'] = compound_interest.round_decimal(result['initial_balance'], 2)

    else:
        # For GET request, provide default form data
        default_data = calculator.get_default_form_data()
        form_data = {
            'initial_balance': str(default_data['initial_balance']),
            'annual_interest_rate': str(default_data['annual_interest_rate']),
            'duration_years': str(default_data['duration_years']),
            'deposit_frequency': str(default_data['deposit_frequency']),
            'periodic_deposit': str(default_data['periodic_deposit']),
            'deposit_at_beginning': default_data['deposit_at_beginning'],
            'goal_balance': str(default_data['goal_balance']),
            'calculate_for': default_data['calculate_for']
        }
        # On initial load, calculate final balance with defaults to populate graph
        default_calc_data = {
            'principal': default_data['initial_balance'],
            'annual_rate': default_data['annual_interest_rate'],
            'years': default_data['duration_years'],
            'periods_per_year': default_data['deposit_frequency'],
            'periodic_deposit': default_data['periodic_deposit'],
            'deposit_at_beginning': default_data['deposit_at_beginning'],
            'calculate_for': 'final_balance'
        }
        result = calculator.calculate(default_calc_data)


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


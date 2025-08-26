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
    """Renders the homepage."""
    return render_template('index.html')

@app.route('/compound', methods=['GET', 'POST'])
def compound():
    """Handles the Compound Interest Calculator page."""
    calculator = CompoundInterestWebCalculator()
    result = None
    # Initialize form_data with default numeric values for the GET request
    form_data = calculator.get_default_form_data()

    if request.method == 'POST':
        # On POST, process the form data from the request
        processed_data, form_data_from_post, error = calculator.process_form_data(request.form)
        
        # Use the submitted data to repopulate the form
        form_data = form_data_from_post

        if error:
            result = error
        else:
            # If data is valid, perform the calculation
            result = calculator.calculate(processed_data)
            # Update the form_data dict with the correctly typed numeric values from processed_data.
            # This ensures that when the template formats these values for the results summary,
            # it receives numbers, not strings, preventing the ValueError.
            # The original string values for <select> inputs are preserved.
            if processed_data:
                form_data.update(processed_data)

    return render_template('compound.html', result=result, form_data=form_data)


@app.route('/dca', methods=['GET', 'POST'])
def dca():
    """Handles the DCA Strategy Optimizer page."""
    calculator = DCAOptimizerWebCalculator()
    result = None
    form_data = calculator.get_default_form_data()

    if request.method == 'POST':
        processed_data, form_data, error = calculator.process_form_data(request.form)
        if error:
            result = error
        else:
            result = calculator.calculate(processed_data)

    return render_template('dca.html', result=result, form_data=form_data)

@app.route('/capital_gains', methods=['GET', 'POST'])
def capital_gains_calc():
    """Handles the Capital Gains Opportunity Cost Calculator page."""
    calculator = CapitalGainsWebCalculator()
    result = None
    form_data = calculator.get_default_form_data()

    if request.method == 'POST':
        processed_data, form_data, error = calculator.process_form_data(request.form)
        if error:
            result = error
        else:
            result = calculator.calculate(processed_data)

    return render_template('capital_gains.html', result=result, form_data=form_data)

@app.route('/options', methods=['GET', 'POST'])
def options():
    """Handles the Options Strategy Calculator page."""
    calculator = OptionsStrategyWebCalculator()
    result = None
    form_data = calculator.get_default_form_data()

    if request.method == 'POST':
        processed_data, form_data, error = calculator.process_form_data(request.form)
        if error:
            result = error
        else:
            result = calculator.calculate(processed_data)

    return render_template('options.html', result=result, form_data=form_data)

if __name__ == '__main__':
    app.run(debug=True)

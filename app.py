from flask import Flask, render_template, request
from calculators import capital_gains, compound_interest, dca_optimizer, options_strategy
import json

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/compound', methods=['GET', 'POST'])
def compound():
    result = None
    form_data = {}
    if request.method == 'POST':
        try:
            form_data = request.form.to_dict()
            initial_balance = float(form_data['initial_balance'])
            periodic_deposit = float(form_data['periodic_deposit'])
            frequency = int(form_data['frequency'])
            deposit_timing = form_data['deposit_timing'] == 'start'
            interest_rate = float(form_data['interest_rate'])
            duration = int(form_data['duration'])

            result = compound_interest.calculate_future_value_and_history(
                initial_balance, interest_rate, duration, frequency, periodic_deposit, deposit_timing
            )
            # Check for error returned by the calculator function
            if result and 'error' in result:
                # If the result is an error dict, use it directly
                pass 
            else:
                # Otherwise, it's successful data
                # The chart_data is already in the result dictionary, no further processing needed
                pass

        except (ValueError, KeyError) as e:
            # Catch general form submission errors (e.g., non-numeric input for float fields)
            result = {'error': f"Please check your inputs. Ensure all fields are filled with valid numbers."}
        except Exception as e:
            # Catch any other unexpected errors
            result = {'error': f"An unexpected error occurred: {e}. Please try again."}

    return render_template('compound.html', result=result, form_data=form_data)


@app.route('/dca', methods=['GET', 'POST'])
def dca():
    result = None
    form_data = {}
    if request.method == 'POST':
        try:
            form_data = request.form.to_dict()
            total_capital = float(form_data['total_capital'])
            share_price = float(form_data['share_price'])
            commission_fee = float(form_data['commission_fee'])
            annualized_volatility = float(form_data['annualized_volatility'])

            result = dca_optimizer.calculate_optimal_dca(
                total_capital, share_price, commission_fee, annualized_volatility
            )
            # No further processing needed, result already contains error or data
        except (ValueError, KeyError) as e:
             result = {'error': f"Please check your inputs for the DCA Optimizer. Ensure all fields are filled with valid numbers."}
        except Exception as e:
            result = {'error': f"An unexpected error occurred in DCA Optimizer: {e}. Please try again."}

    return render_template('dca.html', result=result, form_data=form_data)

@app.route('/capital_gains', methods=['GET', 'POST'])
def capital_gains_calc():
    result = None
    form_data = {}
    if request.method == 'POST':
        try:
            form_data = request.form.to_dict()
            current_value = float(form_data['current_value'])
            cost_basis = float(form_data['cost_basis'])
            tax_rate = float(form_data['tax_rate'])

            result = capital_gains.calculate_required_return(
                current_value, cost_basis, tax_rate
            )
            # No further processing needed, result already contains error or data
        except (ValueError, KeyError) as e:
            result = {'error': f"Please check your inputs for Capital Gains. Ensure all fields are filled with valid numbers."}
        except Exception as e:
            result = {'error': f"An unexpected error occurred in Capital Gains: {e}. Please try again."}

    return render_template('capital_gains.html', result=result, form_data=form_data)

@app.route('/options', methods=['GET', 'POST'])
def options():
    result = None
    form_data = {}
    calculation_type = request.form.get('calculation_type')

    if request.method == 'POST':
        try:
            form_data = request.form.to_dict()
            if calculation_type == 'expected_move':
                stock_price = float(form_data['stock_price_move'])
                call_price = float(form_data['call_price_move'])
                put_price = float(form_data['put_price_move'])
                result = options_strategy.calculate_expected_move(
                    stock_price, call_price, put_price
                )
            elif calculation_type == 'sell_vs_exercise':
                stock_price = float(form_data['stock_price_exercise'])
                strike_price = float(form_data['strike_price_exercise'])
                option_premium = float(form_data['premium_exercise'])
                result = options_strategy.compare_sell_vs_exercise(
                    stock_price, strike_price, option_premium
                )
            
            if result:
                result['type'] = calculation_type # Ensure 'type' is set for front-end conditional rendering
            
        except (ValueError, KeyError) as e:
            result = {'error': f"Please check your inputs for the Options Calculator. Ensure all fields are filled with valid numbers.", 'type': calculation_type}
        except Exception as e:
            result = {'error': f"An unexpected error occurred in Options Calculator: {e}. Please try again.", 'type': calculation_type}

    return render_template('options.html', result=result, form_data=form_data)

if __name__ == '__main__':
    app.run(debug=True)
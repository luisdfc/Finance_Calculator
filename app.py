from flask import Flask, render_template, request
from calculators import capital_gains, compound_interest, dca_optimizer, options_strategy
import json

app = Flask(__name__)

# Helper to convert plot to JSON
def plot_to_json(plot_html):
    """Extracts the data from a Plotly HTML div and returns it as JSON for Chart.js."""
    if not plot_html:
        return None
    try:
        start_str = 'Plotly.newPlot("plot", '
        end_str = ', {"displayModeBar": false});'
        start_index = plot_html.find(start_str)
        if start_index == -1:
            return None

        start_index += len(start_str)
        end_index = plot_html.find(end_str, start_index)

        json_str = plot_html[start_index:end_index]
        data = json.loads(json_str)

        chartjs_data = {
            'labels': data[0].get('x', []),
            'datasets': []
        }

        for trace in data:
            chartjs_data['datasets'].append({
                'label': trace.get('name', ''),
                'data': trace.get('y', []),
                'backgroundColor': get_chart_color(trace.get('name')),
                'borderColor': get_chart_color(trace.get('name')),
                'borderWidth': 1
            })

        return json.dumps(chartjs_data)
    except (json.JSONDecodeError, IndexError) as e:
        print(f"Error parsing plot HTML: {e}")
        return None

def get_chart_color(label):
    """Assigns specific colors to chart datasets for the dark theme."""
    if 'Inicial' in label:
        return 'rgba(59, 130, 246, 0.7)' # Blue
    if 'Aportaciones' in label:
        return 'rgba(16, 185, 129, 0.7)' # Green
    if 'Intereses' in label:
        return 'rgba(245, 158, 11, 0.7)' # Amber
    return 'rgba(107, 114, 128, 0.7)' # Grey


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
            if result and result.get('plot_html'):
                result['chart_json'] = plot_to_json(result['plot_html'])

        except (ValueError, KeyError) as e:
            result = {'error': f"Invalid input. Please ensure all fields are filled correctly. Error: {e}"}

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
        except (ValueError, KeyError) as e:
             result = {'error': f"Invalid input. Please ensure all fields are filled correctly. Error: {e}"}

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
        except (ValueError, KeyError) as e:
            result = {'error': f"Invalid input. Please ensure all fields are filled correctly. Error: {e}"}

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
                result['type'] = calculation_type
        except (ValueError, KeyError) as e:
            result = {'error': f"Invalid input. Please ensure all fields are filled correctly. Error: {e}", 'type': calculation_type}

    return render_template('options.html', result=result, form_data=form_data)

if __name__ == '__main__':
    app.run(debug=True)
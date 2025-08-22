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
    if request.method == 'POST':
        try:
            initial_balance = float(request.form['initial_balance'])
            periodic_deposit = float(request.form['periodic_deposit'])
            frequency = int(request.form['frequency'])
            deposit_timing = request.form['deposit_timing'] == 'start'
            interest_rate = float(request.form['interest_rate'])
            duration = int(request.form['duration'])
            
            result = compound_interest.calculate_future_value_and_history(
                initial_balance, interest_rate, duration, frequency, periodic_deposit, deposit_timing
            )
            if result and result.get('plot_html'):
                result['chart_json'] = plot_to_json(result['plot_html'])

        except (ValueError, KeyError) as e:
            result = {'error': f"Invalid input. Please ensure all fields are filled correctly. Error: {e}"}
            
    return render_template('compound.html', result=result)


@app.route('/dca', methods=['GET', 'POST'])
def dca():
    result = None
    if request.method == 'POST':
        try:
            total_capital = float(request.form['total_capital'])
            share_price = float(request.form['share_price'])
            commission_fee = float(request.form['commission_fee'])
            annualized_volatility = float(request.form['annualized_volatility'])
            
            result = dca_optimizer.calculate_optimal_dca(
                total_capital, share_price, commission_fee, annualized_volatility
            )
        except (ValueError, KeyError) as e:
             result = {'error': f"Invalid input. Please ensure all fields are filled correctly. Error: {e}"}

    return render_template('dca.html', result=result)

@app.route('/capital_gains', methods=['GET', 'POST'])
def capital_gains_calc():
    result = None
    if request.method == 'POST':
        try:
            current_value = float(request.form['current_value'])
            cost_basis = float(request.form['cost_basis'])
            tax_rate = float(request.form['tax_rate'])
            
            result = capital_gains.calculate_required_return(
                current_value, cost_basis, tax_rate
            )
        except (ValueError, KeyError) as e:
            result = {'error': f"Invalid input. Please ensure all fields are filled correctly. Error: {e}"}
            
    return render_template('capital_gains.html', result=result)

@app.route('/options', methods=['GET', 'POST'])
def options():
    result = None
    calculation_type = request.form.get('calculation_type')

    if request.method == 'POST':
        try:
            if calculation_type == 'expected_move':
                stock_price = float(request.form['stock_price_move'])
                call_price = float(request.form['call_price_move'])
                put_price = float(request.form['put_price_move'])
                result = options_strategy.calculate_expected_move(
                    stock_price, call_price, put_price
                )
            elif calculation_type == 'sell_vs_exercise':
                stock_price = float(request.form['stock_price_exercise'])
                strike_price = float(request.form['strike_price_exercise'])
                option_premium = float(request.form['premium_exercise'])
                result = options_strategy.compare_sell_vs_exercise(
                    stock_price, strike_price, option_premium
                )
            if result:
                result['type'] = calculation_type
        except (ValueError, KeyError) as e:
            result = {'error': f"Invalid input. Please ensure all fields are filled correctly. Error: {e}", 'type': calculation_type}

    return render_template('options.html', result=result)

if __name__ == '__main__':
    app.run(debug=True)
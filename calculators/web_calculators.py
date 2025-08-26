# calculators/web_calculators.py

from decimal import Decimal, InvalidOperation
from calculators import compound_interest

class BaseWebCalculator:
    """Base class for web calculators to handle common patterns."""
    def process_form_data(self, form):
        """Processes and validates form data, converting to appropriate types."""
        raise NotImplementedError("Subclasses must implement process_form_data method.")

    def calculate(self, processed_data):
        """Performs the calculation using the processed data."""
        raise NotImplementedError("Subclasses must implement calculate method.")

    def get_default_form_data(self):
        """Returns default form data for initial GET requests."""
        raise NotImplementedError("Subclasses must implement get_default_form_data method.")

class CompoundInterestWebCalculator(BaseWebCalculator):
    def get_default_form_data(self):
        """Returns default values for the compound interest form."""
        return {
            'initial_balance': Decimal('10000'),
            'annual_interest_rate': Decimal('5'),
            'duration_years': Decimal('10'),
            'deposit_frequency': Decimal('12'), # Monthly
            'periodic_deposit': Decimal('100'),
            'deposit_at_beginning': False,
            'goal_balance': Decimal('20000'), # Default goal for inverse calculations
            'calculate_for': 'final_balance' # Default calculation type
        }

    def process_form_data(self, form):
        """
        Processes and validates form data for compound interest calculations.
        Converts all numeric inputs to Decimal.
        """
        form_data = self.get_default_form_data()
        input_error = None
        processed_data = {}

        # Determine which field to calculate
        calculate_for = form.get('calculate_for', 'final_balance')
        form_data['calculate_for'] = calculate_for

        try:
            # Always try to get values for all fields, even if some are to be calculated
            # We'll set the value to None/0 for the field being calculated.
            
            # Initial Balance
            initial_balance_str = form.get('initial_balance', '').replace(',', '')
            if initial_balance_str and calculate_for != 'initial_balance':
                processed_data['principal'] = Decimal(initial_balance_str)
            else:
                processed_data['principal'] = Decimal('0') # Default for calculation, will be ignored if solving for it
            form_data['initial_balance'] = initial_balance_str # Keep original string for form display

            # Annual Interest Rate
            annual_interest_rate_str = form.get('annual_interest_rate', '').replace(',', '')
            if annual_interest_rate_str and calculate_for != 'annual_interest_rate':
                processed_data['annual_rate'] = Decimal(annual_interest_rate_str)
            else:
                processed_data['annual_rate'] = Decimal('0')
            form_data['annual_interest_rate'] = annual_interest_rate_str

            # Duration (Years)
            duration_years_str = form.get('duration_years', '').replace(',', '')
            if duration_years_str and calculate_for != 'duration_years':
                processed_data['years'] = Decimal(duration_years_str)
            else:
                processed_data['years'] = Decimal('0')
            form_data['duration_years'] = duration_years_str

            # Deposit Frequency
            deposit_frequency_str = form.get('deposit_frequency', '').replace(',', '')
            if deposit_frequency_str:
                processed_data['periods_per_year'] = Decimal(deposit_frequency_str)
            else:
                processed_data['periods_per_year'] = Decimal('12') # Default if not provided, not calculated
            form_data['deposit_frequency'] = deposit_frequency_str


            # Periodic Deposit
            periodic_deposit_str = form.get('periodic_deposit', '').replace(',', '')
            if periodic_deposit_str and calculate_for != 'periodic_deposit':
                processed_data['periodic_deposit'] = Decimal(periodic_deposit_str)
            else:
                processed_data['periodic_deposit'] = Decimal('0')
            form_data['periodic_deposit'] = periodic_deposit_str

            # Deposit at Beginning
            processed_data['deposit_at_beginning'] = form.get('deposit_at_beginning') == 'on'
            form_data['deposit_at_beginning'] = processed_data['deposit_at_beginning']

            # Goal Balance (only for inverse calculations)
            goal_balance_str = form.get('goal_balance', '').replace(',', '')
            if goal_balance_str:
                processed_data['goal_balance'] = Decimal(goal_balance_str)
            else:
                processed_data['goal_balance'] = Decimal('0') # Default
            form_data['goal_balance'] = goal_balance_str


            # Check for missing values needed for calculation
            # We specifically set the value to 0 if it's the one we're calculating for
            # The calculation functions in compound_interest.py will handle which parameter is 'missing'
            # and use a sentinel value like 0, or accept a missing argument.
            # Here, we ensure that the required values (that are *not* being calculated) are present and valid.

            if calculate_for != 'final_balance' and not processed_data.get('goal_balance', Decimal('0')) > 0:
                 input_error = {"error": "Please enter a positive Goal Balance when calculating for other variables."}

            if calculate_for == 'initial_balance' and not (processed_data.get('years') > 0 and processed_data.get('periods_per_year') > 0):
                input_error = {"error": "Duration and Deposit Frequency must be positive to calculate Initial Balance."}
            
            if calculate_for == 'periodic_deposit' and not (processed_data.get('years') > 0 and processed_data.get('periods_per_year') > 0):
                 input_error = {"error": "Duration and Deposit Frequency must be positive to calculate Periodic Deposit."}

            if calculate_for == 'duration_years' and not (processed_data.get('principal', Decimal('0')) >= 0 and processed_data.get('periods_per_year') > 0):
                input_error = {"error": "Initial Balance and Deposit Frequency must be valid to calculate Duration."}

            if calculate_for == 'annual_interest_rate' and not (processed_data.get('principal', Decimal('0')) >= 0 and processed_data.get('years') > 0 and processed_data.get('periods_per_year') > 0):
                input_error = {"error": "Initial Balance, Duration, and Deposit Frequency must be valid to calculate Interest Rate."}

            if calculate_for != 'final_balance':
                # For inverse calculations, we need at least some growth mechanism
                if processed_data['annual_rate'] == 0 and processed_data['periodic_deposit'] == 0 and processed_data['principal'] < processed_data['goal_balance']:
                    input_error = {"error": "With zero interest and zero periodic deposits, goal is unreachable without more initial capital."}


        except InvalidOperation:
            input_error = {"error": "Invalid numeric input. Please enter valid numbers."}
        except Exception as e:
            input_error = {"error": f"An unexpected error occurred during input processing: {e}"}

        return processed_data, form_data, input_error

    def calculate(self, processed_data):
        """
        Dispatches to the correct compound interest calculation function
        based on what the user wants to calculate.
        """
        calculate_for = processed_data.get('calculate_for', 'final_balance')
        
        principal = processed_data.get('principal')
        annual_rate = processed_data.get('annual_rate')
        years = processed_data.get('years')
        periods_per_year = processed_data.get('periods_per_year')
        periodic_deposit = processed_data.get('periodic_deposit')
        deposit_at_beginning = processed_data.get('deposit_at_beginning')
        goal_balance = processed_data.get('goal_balance')

        if calculate_for == 'final_balance':
            return compound_interest.calculate_final_balance_and_history(
                principal=principal,
                annual_rate=annual_rate,
                years=years,
                periods_per_year=periods_per_year,
                periodic_deposit=periodic_deposit,
                deposit_at_beginning=deposit_at_beginning
            )
        elif calculate_for == 'duration_years':
            return compound_interest.calculate_time_to_reach_goal(
                principal=principal,
                annual_rate=annual_rate,
                periodic_deposit=periodic_deposit,
                periods_per_year=periods_per_year,
                deposit_at_beginning=deposit_at_beginning,
                goal_balance=goal_balance
            )
        elif calculate_for == 'periodic_deposit':
            return compound_interest.calculate_periodic_deposit_needed(
                principal=principal,
                annual_rate=annual_rate,
                years=years,
                periods_per_year=periods_per_year,
                deposit_at_beginning=deposit_at_beginning,
                goal_balance=goal_balance
            )
        elif calculate_for == 'annual_interest_rate':
            return compound_interest.calculate_interest_rate_needed(
                principal=principal,
                years=years,
                periods_per_year=periods_per_year,
                periodic_deposit=periodic_deposit,
                deposit_at_beginning=deposit_at_beginning,
                goal_balance=goal_balance
            )
        elif calculate_for == 'initial_balance':
            return compound_interest.calculate_initial_balance_needed(
                annual_rate=annual_rate,
                years=years,
                periods_per_year=periods_per_year,
                periodic_deposit=periodic_deposit,
                deposit_at_beginning=deposit_at_beginning,
                goal_balance=goal_balance
            )
        else:
            return {"error": "Invalid calculation type selected."}


class DCAOptimizerWebCalculator(WebCalculator):
    """Handles logic for the DCA Optimizer Calculator."""

    def get_default_form_data(self):
        return {
            'total_capital': 1000,
            'share_price': 10,
            'commission_fee': 5,
            'annualized_volatility': 0.60
        }

    def process_form_data(self, form):
        form_data = form.to_dict()
        try:
            total_capital = self._safe_decimal_conversion(form_data.get('total_capital'))
            share_price = self._safe_decimal_conversion(form_data.get('share_price'))
            commission_fee = self._safe_decimal_conversion(form_data.get('commission_fee'))
            annualized_volatility = self._safe_decimal_conversion(form_data.get('annualized_volatility'))

            if None in [total_capital, share_price, commission_fee, annualized_volatility]:
                return None, form_data, {"error": "All fields must be valid numbers."}

            return {
                'total_capital': total_capital,
                'share_price': share_price,
                'commission_fee': commission_fee,
                'annualized_volatility': annualized_volatility
            }, form_data, None
        except Exception:
            return None, form_data, {"error": "Invalid input. Please ensure all fields are filled correctly."}

    def calculate(self, processed_data):
        result = dca_optimizer.calculate_optimal_dca(
            processed_data['total_capital'],
            processed_data['share_price'],
            processed_data['commission_fee'],
            processed_data['annualized_volatility']
        )
        if 'error' in result:
            return result
        
        # Convert Decimal values back to float
        for key in ['trigger_percentage', 'capital_per_trade']:
            if key in result and isinstance(result[key], Decimal):
                result[key] = float(result[key])
        # optimal_trades is an int, no conversion needed

        return result

class CapitalGainsWebCalculator(WebCalculator):
    """Handles logic for the Capital Gains Opportunity Cost Calculator."""

    def get_default_form_data(self):
        return {
            'current_value': 1500,
            'cost_basis': 1000,
            'tax_rate': 0.19
        }

    def process_form_data(self, form):
        form_data = form.to_dict()
        try:
            current_value = self._safe_decimal_conversion(form_data.get('current_value'))
            cost_basis = self._safe_decimal_conversion(form_data.get('cost_basis'))
            tax_rate = self._safe_decimal_conversion(form_data.get('tax_rate'))

            if None in [current_value, cost_basis, tax_rate]:
                return None, form_data, {"error": "All fields must be valid numbers."}
            
            return {
                'current_value': current_value,
                'cost_basis': cost_basis,
                'tax_rate': tax_rate
            }, form_data, None
        except Exception:
            return None, form_data, {"error": "Invalid input. Please ensure all fields are filled correctly."}

    def calculate(self, processed_data):
        result = capital_gains.calculate_required_return(
            processed_data['current_value'],
            processed_data['cost_basis'],
            processed_data['tax_rate']
        )
        if 'error' in result or 'note' in result:
            return result
        
        # Generate chart data
        chart_data = capital_gains.generate_tax_rate_chart_data(
            processed_data['current_value'],
            processed_data['cost_basis']
        )
        result['chart_data'] = chart_data # Add chart data to result
        
        # Convert Decimal values back to float
        for key in ['capital_gain', 'tax_cost', 'post_tax_proceeds', 'required_return']:
            if key in result and isinstance(result[key], Decimal):
                result[key] = float(result[key])

        return result


class OptionsStrategyWebCalculator(WebCalculator):
    """Handles logic for the Options Strategy Calculator."""

    def get_default_form_data(self):
        return {
            'calculation_type': 'expected_move', # Default to expected move
            'stock_price_move': 150,
            'call_price_move': 5,
            'put_price_move': 5,
            'stock_price_exercise': 165,
            'strike_price_exercise': 155,
            'premium_exercise': 10.50
        }

    def process_form_data(self, form):
        form_data = form.to_dict()
        calculation_type = form_data.get('calculation_type')
        processed_data = {'calculation_type': calculation_type}

        try:
            if calculation_type == 'expected_move':
                stock_price = self._safe_decimal_conversion(form_data.get('stock_price_move'))
                call_price = self._safe_decimal_conversion(form_data.get('call_price_move'))
                put_price = self._safe_decimal_conversion(form_data.get('put_price_move'))
                if None in [stock_price, call_price, put_price]:
                     return None, form_data, {"error": "All fields for Market's Expected Move must be valid numbers."}
                processed_data.update({
                    'stock_price': stock_price,
                    'call_price': call_price,
                    'put_price': put_price
                })
            elif calculation_type == 'sell_vs_exercise':
                stock_price = self._safe_decimal_conversion(form_data.get('stock_price_exercise'))
                strike_price = self._safe_decimal_conversion(form_data.get('strike_price_exercise'))
                option_premium = self._safe_decimal_conversion(form_data.get('premium_exercise'))
                if None in [stock_price, strike_price, option_premium]:
                    return None, form_data, {"error": "All fields for Sell vs. Exercise must be valid numbers."}
                processed_data.update({
                    'stock_price': stock_price,
                    'strike_price': strike_price,
                    'option_premium': option_premium
                })
            else:
                return None, form_data, {"error": "Invalid calculation type selected."}
            
            return processed_data, form_data, None
        except Exception:
            return None, form_data, {"error": "Invalid input. Please ensure all fields are filled correctly for the selected options calculation."}

    def calculate(self, processed_data):
        calculation_type = processed_data['calculation_type']
        result = {}
        if calculation_type == 'expected_move':
            result = options_strategy.calculate_expected_move(
                processed_data['stock_price'],
                processed_data['call_price'],
                processed_data['put_price']
            )
        elif calculation_type == 'sell_vs_exercise':
            result = options_strategy.compare_sell_vs_exercise(
                processed_data['stock_price'],
                processed_data['strike_price'],
                processed_data['option_premium']
            )
        
        if result:
            result['type'] = calculation_type
            # Convert Decimal values back to float for all relevant keys
            for key in ['expected_move', 'expected_percentage', 'upper_bound', 'lower_bound', 
                        'profit_from_selling', 'profit_from_exercising', 'extrinsic_value']:
                if key in result and isinstance(result[key], Decimal):
                    result[key] = float(result[key])
        return result
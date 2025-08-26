# calculators/web_calculators.py (Updated for Compound Interest multi-goal)

from decimal import Decimal, InvalidOperation # Import Decimal and InvalidOperation
from . import capital_gains, compound_interest, dca_optimizer, options_strategy

class WebCalculator:
    """
    Base class for all web-based financial calculators.
    Provides common utility methods for handling form data and errors.
    """
    def _safe_decimal_conversion(self, value, default_value=None):
        """Safely converts a string value to Decimal, handling potential errors."""
        try:
            # Attempt to strip spaces and replace comma with dot for European number format
            if value is None or value == '': # Handle empty strings for optional fields
                return default_value
            if isinstance(value, str):
                value = value.strip().replace(',', '.')
            return Decimal(value)
        except (InvalidOperation, TypeError):
            return default_value

    def _safe_int_conversion(self, value, default_value=None):
        """Safely converts a string value to int, handling potential errors."""
        try:
            if value is None or value == '': # Handle empty strings for optional fields
                return default_value
            return int(value)
        except (ValueError, TypeError):
            return default_value

    def get_default_form_data(self):
        """Returns default values for the form fields."""
        raise NotImplementedError("Subclasses must implement get_default_form_data")

    def process_form_data(self, form):
        """
        Extracts and converts form data.
        Returns a tuple: (processed_data, form_data_for_template, error_message).
        """
        raise NotImplementedError("Subclasses must implement process_form_data")

    def calculate(self, processed_data):
        """
        Performs the calculation using the processed data.
        Returns the result dictionary (which may contain an 'error' or 'note' key).
        """
        raise NotImplementedError("Subclasses must implement calculate")

class CompoundInterestWebCalculator(WebCalculator):
    """Handles logic for the Compound Interest Calculator."""

    def get_default_form_data(self):
        return {
            'calculation_type': 'final_balance', # Default calculation
            'initial_balance': 1000,
            'periodic_deposit': 100,
            'frequency': '12', # Default to Monthly
            'deposit_timing': 'start',
            'interest_rate': 7,
            'duration': 10,
            'target_balance': None # For when final balance is an input
        }

    def process_form_data(self, form):
        form_data = form.to_dict()
        calculation_type = form_data.get('calculation_type', 'final_balance')
        
        # All fields are treated as potentially empty based on calculation_type
        initial_balance_raw = form_data.get('initial_balance')
        periodic_deposit_raw = form_data.get('periodic_deposit')
        frequency_raw = form_data.get('frequency')
        interest_rate_raw = form_data.get('interest_rate')
        duration_raw = form_data.get('duration')
        target_balance_raw = form_data.get('target_balance')

        # Convert all to Decimal or int, allowing None for the field to be calculated
        initial_balance = self._safe_decimal_conversion(initial_balance_raw)
        periodic_deposit = self._safe_decimal_conversion(periodic_deposit_raw)
        frequency = self._safe_int_conversion(frequency_raw)
        deposit_timing = form_data.get('deposit_timing') == 'start'
        interest_rate = self._safe_decimal_conversion(interest_rate_raw)
        duration = self._safe_int_conversion(duration_raw)
        target_balance = self._safe_decimal_conversion(target_balance_raw)

        processed_data = {
            'calculation_type': calculation_type,
            'initial_balance': initial_balance,
            'periodic_deposit': periodic_deposit,
            'frequency': frequency,
            'deposit_timing': deposit_timing,
            'interest_rate': interest_rate,
            'duration': duration,
            'target_balance': target_balance
        }
        
        errors = []
        # Validate based on calculation_type
        if calculation_type == 'final_balance':
            if None in [initial_balance, periodic_deposit, frequency, interest_rate, duration]:
                errors.append("All fields must be valid numbers to calculate Final Balance.")
            if initial_balance is not None and initial_balance < 0: errors.append("Initial Balance cannot be negative.")
            if periodic_deposit is not None and periodic_deposit < 0: errors.append("Periodic Deposit cannot be negative.")
            if interest_rate is not None and interest_rate < 0: errors.append("Annual Interest Rate cannot be negative.")
            if duration is not None and duration <= 0: errors.append("Duration (Years) must be a positive integer.")
            if frequency is not None and frequency <= 0: errors.append("Deposit Frequency must be at least once a year.")

        elif calculation_type == 'years':
            if None in [initial_balance, periodic_deposit, frequency, interest_rate, target_balance]:
                errors.append("All fields (except Duration) must be valid numbers to calculate Duration.")
            if initial_balance is not None and initial_balance < 0: errors.append("Initial Balance cannot be negative.")
            if periodic_deposit is not None and periodic_deposit < 0: errors.append("Periodic Deposit cannot be negative.")
            if interest_rate is not None and interest_rate < 0: errors.append("Annual Interest Rate cannot be negative.")
            if target_balance is not None and target_balance <= 0: errors.append("Target Balance must be a positive number.")
            if frequency is not None and frequency <= 0: errors.append("Deposit Frequency must be at least once a year.")
            # Ensure at least one growth factor is present if initial balance < target
            if initial_balance is not None and target_balance is not None and initial_balance < target_balance:
                if (periodic_deposit == 0 or periodic_deposit is None) and (interest_rate == 0 or interest_rate is None):
                     errors.append("To reach a target balance, you need either periodic deposits or an interest rate (or both).")

        elif calculation_type == 'periodic_deposit':
            if None in [initial_balance, frequency, interest_rate, duration, target_balance]:
                errors.append("All fields (except Periodic Deposit) must be valid numbers to calculate Periodic Deposit.")
            if initial_balance is not None and initial_balance < 0: errors.append("Initial Balance cannot be negative.")
            if interest_rate is not None and interest_rate < 0: errors.append("Annual Interest Rate cannot be negative.")
            if duration is not None and duration <= 0: errors.append("Duration (Years) must be a positive integer.")
            if target_balance is not None and target_balance <= 0: errors.append("Target Balance must be a positive number.")
            if frequency is not None and frequency <= 0: errors.append("Deposit Frequency must be at least once a year.")
        
        elif calculation_type == 'interest_rate':
            if None in [initial_balance, periodic_deposit, frequency, duration, target_balance]:
                errors.append("All fields (except Interest Rate) must be valid numbers to calculate Interest Rate.")
            if initial_balance is not None and initial_balance < 0: errors.append("Initial Balance cannot be negative.")
            if periodic_deposit is not None and periodic_deposit < 0: errors.append("Periodic Deposit cannot be negative.")
            if duration is not None and duration <= 0: errors.append("Duration (Years) must be a positive integer.")
            if target_balance is not None and target_balance <= 0: errors.append("Target Balance must be a positive number.")
            if frequency is not None and frequency <= 0: errors.append("Deposit Frequency must be at least once a year.")

        elif calculation_type == 'initial_balance':
            if None in [periodic_deposit, frequency, interest_rate, duration, target_balance]:
                errors.append("All fields (except Initial Balance) must be valid numbers to calculate Initial Balance.")
            if periodic_deposit is not None and periodic_deposit < 0: errors.append("Periodic Deposit cannot be negative.")
            if interest_rate is not None and interest_rate < 0: errors.append("Annual Interest Rate cannot be negative.")
            if duration is not None and duration <= 0: errors.append("Duration (Years) must be a positive integer.")
            if target_balance is not None and target_balance <= 0: errors.append("Target Balance must be a positive number.")
            if frequency is not None and frequency <= 0: errors.append("Deposit Frequency must be at least once a year.")
        
        else:
            errors.append("Invalid calculation type selected.")

        if errors:
            return None, form_data, {"error": " ".join(errors)}
            
        return processed_data, form_data, None

    def calculate(self, processed_data):
        calculation_type = processed_data['calculation_type']
        result = {}

        try:
            if calculation_type == 'final_balance':
                result = compound_interest.calculate_final_balance_and_history(
                    processed_data['initial_balance'],
                    processed_data['interest_rate'],
                    processed_data['duration'],
                    processed_data['frequency'],
                    processed_data['periodic_deposit'],
                    processed_data['deposit_timing']
                )
            elif calculation_type == 'years':
                result = compound_interest.calculate_time_to_reach_goal(
                    processed_data['initial_balance'],
                    processed_data['interest_rate'],
                    processed_data['periodic_deposit'],
                    processed_data['frequency'],
                    processed_data['deposit_timing'],
                    processed_data['target_balance']
                )
            elif calculation_type == 'periodic_deposit':
                result = compound_interest.calculate_periodic_deposit_needed(
                    processed_data['initial_balance'],
                    processed_data['interest_rate'],
                    processed_data['duration'],
                    processed_data['frequency'],
                    processed_data['deposit_timing'],
                    processed_data['target_balance']
                )
            elif calculation_type == 'interest_rate':
                result = compound_interest.calculate_interest_rate_needed(
                    processed_data['initial_balance'],
                    processed_data['duration'],
                    processed_data['frequency'],
                    processed_data['periodic_deposit'],
                    processed_data['deposit_timing'],
                    processed_data['target_balance']
                )
            elif calculation_type == 'initial_balance':
                result = compound_interest.calculate_initial_balance_needed(
                    processed_data['interest_rate'],
                    processed_data['duration'],
                    processed_data['frequency'],
                    processed_data['periodic_deposit'],
                    processed_data['deposit_timing'],
                    processed_data['target_balance']
                )
            else:
                return {"error": "Invalid calculation type specified."}

            if 'error' in result or 'note' in result:
                return result
            
            # Convert Decimal values in the result dictionary and chart_data back to float for JSON serialization
            for key in ['final_balance', 'principal', 'total_deposits', 'interest_earned', 
                        'periodic_deposit', 'initial_balance']:
                if key in result and isinstance(result[key], Decimal):
                    result[key] = float(result[key])
            if 'years' in result and isinstance(result['years'], Decimal):
                result['years'] = float(result['years'])
            if 'interest_rate' in result and isinstance(result['interest_rate'], Decimal):
                result['interest_rate'] = float(result['interest_rate'])
            
            if 'chart_data' in result and result['chart_data']:
                for dataset in result['chart_data']['datasets']:
                    dataset['data'] = [float(val) if isinstance(val, Decimal) else val for val in dataset['data']]
            
            return result

        except Exception as e:
            return {"error": f"An unexpected calculation error occurred: {e}. Please check your inputs."}


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

# calculators/web_calculators.py
from decimal import Decimal, InvalidOperation
from . import capital_gains, compound_interest, dca_optimizer, options_strategy

class WebCalculator:
    """
    Base class for all web-based financial calculators.
    Provides common utility methods for handling form data and errors.
    """
    def _safe_decimal_conversion(self, value, default_value=None):
        """Safely converts a string value to Decimal, handling potential errors."""
        try:
            if value is None or value == '':
                return default_value
            if isinstance(value, str):
                value = value.strip().replace(',', '.')
            return Decimal(value)
        except (InvalidOperation, TypeError):
            return default_value

    def _safe_int_conversion(self, value, default_value=None):
        """Safely converts a string value to int, handling potential errors."""
        try:
            if value is None or value == '':
                return default_value
            return int(value)
        except (ValueError, TypeError):
            return default_value

    def _process_simple_form(self, form, field_definitions):
        """
        Generic processor for simple forms where all fields are required decimals.
        `field_definitions` is a list of field names.
        """
        form_data = form.to_dict()
        processed_data = {}
        try:
            for field in field_definitions:
                value = self._safe_decimal_conversion(form_data.get(field))
                if value is None:
                    return None, form_data, {"error": "All fields must be filled with valid numbers."}
                processed_data[field] = value
            return processed_data, form_data, None
        except Exception:
            return None, form_data, {"error": "Invalid input. Please ensure all fields are filled correctly."}

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
            'calculation_type': 'final_balance',
            'initial_balance': 1000,
            'periodic_deposit': 100,
            'frequency': '12',
            'deposit_timing': 'start',
            'interest_rate': 7,
            'duration': 10,
            'target_balance': 20000
        }

    def _validate_compound_interest_inputs(self, data):
        """Performs validation based on the calculation type."""
        errors = []
        calc_type = data['calculation_type']
        
        required_fields = {
            'final_balance': ['initial_balance', 'periodic_deposit', 'frequency', 'interest_rate', 'duration'],
            'years': ['initial_balance', 'periodic_deposit', 'frequency', 'interest_rate', 'target_balance'],
            'periodic_deposit': ['initial_balance', 'frequency', 'interest_rate', 'duration', 'target_balance'],
            'interest_rate': ['initial_balance', 'periodic_deposit', 'frequency', 'duration', 'target_balance'],
            'initial_balance': ['periodic_deposit', 'frequency', 'interest_rate', 'duration', 'target_balance']
        }

        if calc_type in required_fields:
            for field in required_fields[calc_type]:
                if data.get(field) is None:
                    errors.append(f"A valid number for {field.replace('_', ' ').title()} is required.")
            if errors: return errors # Return early if required fields are missing

        # Specific value validations
        if data.get('initial_balance') is not None and data['initial_balance'] < 0: errors.append("Initial Balance cannot be negative.")
        if data.get('periodic_deposit') is not None and data['periodic_deposit'] < 0: errors.append("Periodic Deposit cannot be negative.")
        if data.get('interest_rate') is not None and data['interest_rate'] < 0: errors.append("Annual Interest Rate cannot be negative.")
        if data.get('duration') is not None and data['duration'] <= 0: errors.append("Duration (Years) must be a positive integer.")
        if data.get('frequency') is not None and data['frequency'] <= 0: errors.append("Deposit Frequency must be at least once a year.")
        if data.get('target_balance') is not None and data['target_balance'] <= 0: errors.append("Target Balance must be a positive number.")

        if calc_type == 'years' and data['initial_balance'] is not None and data['target_balance'] is not None and data['initial_balance'] < data['target_balance']:
            if (data.get('periodic_deposit') == 0 or data.get('periodic_deposit') is None) and (data.get('interest_rate') == 0 or data.get('interest_rate') is None):
                errors.append("To reach a target balance, you need either periodic deposits or an interest rate (or both).")
        
        return errors

    def process_form_data(self, form):
        form_data = form.to_dict()
        calculation_type = form_data.get('calculation_type', 'final_balance')
        
        field_definitions = {
            'initial_balance': 'decimal', 'periodic_deposit': 'decimal',
            'frequency': 'int', 'interest_rate': 'decimal',
            'duration': 'int', 'target_balance': 'decimal'
        }

        processed_data = {'calculation_type': calculation_type}
        for field, f_type in field_definitions.items():
            raw_value = form_data.get(field)
            if f_type == 'decimal':
                processed_data[field] = self._safe_decimal_conversion(raw_value)
            elif f_type == 'int':
                processed_data[field] = self._safe_int_conversion(raw_value)
        
        processed_data['deposit_timing'] = form_data.get('deposit_timing') == 'start'

        errors = self._validate_compound_interest_inputs(processed_data)
        
        if errors:
            return None, form_data, {"error": " ".join(errors)}
            
        return processed_data, form_data, None

    def calculate(self, processed_data):
        calculation_type = processed_data['calculation_type']
        
        try:
            calculation_map = {
                'final_balance': compound_interest.calculate_final_balance_and_history,
                'years': compound_interest.calculate_time_to_reach_goal,
                'periodic_deposit': compound_interest.calculate_periodic_deposit_needed,
                'interest_rate': compound_interest.calculate_interest_rate_needed,
                'initial_balance': compound_interest.calculate_initial_balance_needed
            }

            if calculation_type not in calculation_map:
                return {"error": "Invalid calculation type specified."}

            # Map form field names to the parameter names expected by the calculation functions
            parameter_map = {
                'initial_balance': 'principal',
                'interest_rate': 'annual_rate',
                'duration': 'years',
                'frequency': 'periods_per_year',
                'periodic_deposit': 'periodic_deposit',
                'deposit_timing': 'deposit_at_beginning',
                'target_balance': 'goal_balance'
            }

            # Define which form fields are needed for each calculation
            required_form_fields = {
                'final_balance': ['initial_balance', 'interest_rate', 'duration', 'frequency', 'periodic_deposit', 'deposit_timing'],
                'years': ['initial_balance', 'interest_rate', 'periodic_deposit', 'frequency', 'deposit_timing', 'target_balance'],
                'periodic_deposit': ['initial_balance', 'interest_rate', 'duration', 'frequency', 'deposit_timing', 'target_balance'],
                'interest_rate': ['initial_balance', 'duration', 'frequency', 'periodic_deposit', 'deposit_timing', 'target_balance'],
                'initial_balance': ['interest_rate', 'duration', 'frequency', 'periodic_deposit', 'deposit_timing', 'target_balance']
            }

            # Create a new dictionary with the correct parameter names for the specific calculation
            calculation_args = {}
            for field in required_form_fields.get(calculation_type, []):
                if field in processed_data and processed_data[field] is not None:
                    param_name = parameter_map[field]
                    calculation_args[param_name] = processed_data[field]
            
            # Call the appropriate calculation function with the correctly named arguments
            result = calculation_map[calculation_type](**calculation_args)

            if 'error' in result or 'note' in result:
                return result
            
            # Convert Decimal values in the result for JSON serialization
            for key, value in result.items():
                if isinstance(value, Decimal):
                    result[key] = float(value)
            
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
            'annualized_volatility': 0.60,
            'share_type': 'whole',
            'commission_cap': 0.05  # Default to 5%
        }

    def process_form_data(self, form):
        form_data = form.to_dict()
        processed_data = {}
        error = None
        
        try:
            # Process decimal fields
            decimal_fields = ['total_capital', 'share_price', 'commission_fee', 'annualized_volatility', 'commission_cap']
            for field in decimal_fields:
                value = self._safe_decimal_conversion(form_data.get(field))
                if value is None:
                    # Provide a more specific error message
                    return None, form_data, {"error": f"A valid number for '{field.replace('_', ' ').title()}' is required."}
                processed_data[field] = value
            
            # Process the share_type string field
            share_type = form_data.get('share_type', 'whole')
            if share_type not in ['whole', 'fractional']:
                share_type = 'whole' # Default to 'whole' if invalid value
            processed_data['share_type'] = share_type

        except Exception:
            error = {"error": "Invalid input. Please ensure all fields are filled correctly."}

        return processed_data, form_data, error

    def calculate(self, processed_data):
        result = dca_optimizer.calculate_optimal_dca(**processed_data)
        if 'error' in result:
            return result
        
        # Convert all decimal values in the result dictionary to float for JSON compatibility
        for key, value in result.items():
            if isinstance(value, Decimal):
                result[key] = float(value)
        
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
        fields = ['current_value', 'cost_basis', 'tax_rate']
        return self._process_simple_form(form, fields)

    def calculate(self, processed_data):
        result = capital_gains.calculate_required_return(**processed_data)
        if 'error' in result or 'note' in result:
            return result
        
        chart_data = capital_gains.generate_tax_rate_chart_data(
            processed_data['current_value'],
            processed_data['cost_basis']
        )
        result['chart_data'] = chart_data
        
        for key in ['capital_gain', 'tax_cost', 'post_tax_proceeds', 'required_return']:
            if key in result and isinstance(result[key], Decimal):
                result[key] = float(result[key])
        return result


class OptionsStrategyWebCalculator(WebCalculator):
    """Handles logic for the Options Strategy Calculator."""

    def get_default_form_data(self):
        return {
            'calculation_type': 'expected_move',
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
                fields_map = {
                    'stock_price': 'stock_price_move',
                    'call_price': 'call_price_move',
                    'put_price': 'put_price_move'
                }
                error_msg = "All fields for Market's Expected Move must be valid numbers."
            elif calculation_type == 'sell_vs_exercise':
                fields_map = {
                    'stock_price': 'stock_price_exercise',
                    'strike_price': 'strike_price_exercise',
                    'option_premium': 'premium_exercise'
                }
                error_msg = "All fields for Sell vs. Exercise must be valid numbers."
            else:
                return None, form_data, {"error": "Invalid calculation type selected."}

            for key, form_field in fields_map.items():
                value = self._safe_decimal_conversion(form_data.get(form_field))
                if value is None:
                    return None, form_data, {"error": error_msg}
                processed_data[key] = value
            
            return processed_data, form_data, None
        except Exception:
            return None, form_data, {"error": "Invalid input. Please check all fields."}

    def calculate(self, processed_data):
        calculation_type = processed_data.pop('calculation_type')
        
        if calculation_type == 'expected_move':
            result = options_strategy.calculate_expected_move(**processed_data)
        elif calculation_type == 'sell_vs_exercise':
            result = options_strategy.compare_sell_vs_exercise(**processed_data)
        else:
            return {"error": "Invalid calculation type."}
        
        if result:
            result['type'] = calculation_type
            for key, value in result.items():
                if isinstance(value, Decimal):
                    result[key] = float(value)
        return result
def calculate_required_return(current_value, cost_basis, tax_rate):
    """
    Calculates the required return on a new investment to justify
    selling a current one and paying capital gains tax.
    """
    if current_value <= 0:
        return {"error": "Current Investment Value must be a positive number."}
    if cost_basis <= 0:
        return {"error": "Original Cost Basis must be a positive number."}
    if not (0 <= tax_rate < 1):
        return {"error": "Capital Gains Tax Rate must be between 0 (0%) and 1 (100%)."}

    if current_value < cost_basis:
        return {
            "note": "The current value is less than the cost basis, resulting in a capital loss. There is no tax cost, so any new investment with a positive return is technically better."
        }

    capital_gain = current_value - cost_basis
    tax_cost = tax_rate * capital_gain
    post_tax_proceeds = current_value - tax_cost

    if post_tax_proceeds <= 0:
        return {"error": "Post-tax proceeds are zero or less. Cannot calculate a meaningful return because there's no capital left to reinvest after tax."}

    required_return = tax_cost / post_tax_proceeds
    return {
        "capital_gain": capital_gain,
        "tax_cost": tax_cost,
        "post_tax_proceeds": post_tax_proceeds,
        "required_return": required_return
    }
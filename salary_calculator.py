def calculate_tax(income, brackets):
    tax = 0
    previous_limit = 0
    for limit, rate in brackets:
        if income > limit:
            tax += (limit - previous_limit) * rate
        else:
            tax += (income - previous_limit) * rate
            break
        previous_limit = limit
    return tax

def calculate_take_home_salary(annual_salary, province):
    # Federal tax brackets for 2023
    federal_tax_brackets = [
        (53359, 0.15),
        (106717, 0.205),
        (165430, 0.26),
        (235675, 0.29),
        (float('inf'), 0.33)
    ]

    # Provincial tax brackets
    provincial_tax_brackets = {
        'British Columbia': [
            (45654, 0.0506),
            (91310, 0.077),
            (104835, 0.105),
            (127299, 0.1229),
            (172602, 0.147),
            (240716, 0.168),
            (float('inf'), 0.205)
        ],
        'Manitoba': [
            (36842, 0.108),
            (79625, 0.1275),
            (float('inf'), 0.174)
        ]
    }

    # Calculate federal tax
    federal_tax = calculate_tax(annual_salary, federal_tax_brackets)

    # Calculate provincial tax
    provincial_tax = calculate_tax(annual_salary, provincial_tax_brackets.get(province, []))

    # CPP and EI rates for 2023
    cpp_rate = 0.0595
    ei_rate = 0.0163

    # Calculate CPP and EI deductions
    cpp_deduction = min(annual_salary * cpp_rate, 3754.45)  # Max CPP contribution
    ei_deduction = annual_salary * ei_rate

    # Total deductions
    total_deductions = federal_tax + provincial_tax + cpp_deduction + ei_deduction

    # Net (take-home) salary
    take_home_salary = annual_salary - total_deductions

    return take_home_salary

# Example usage
province = "British Columbia"
annual_salary = 60000
take_home_salary = calculate_take_home_salary(annual_salary, province)
print(f"Take-home salary in {province} for an annual salary of ${annual_salary}: ${take_home_salary:.2f}")



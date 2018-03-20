def endowment(salary, isLeast):
    if salary > 23118:
        cardinal = 23118
    elif salary < 3082:
        cardinal = 3082
    else:
        cardinal = salary
    if isLeast:
        cardinal = 3082
    return cardinal * 0.08


def medical(salary, isLeast):
    if salary > 23118:
        cardinal = 23118
    elif salary < 4624:
        cardinal = 4624
    else:
        cardinal = salary
    if isLeast:
        cardinal = 4624
    return cardinal * 0.02 + 3


def unemployment(salary, isLeast):
    if salary > 23118:
        cardinal = 23118
    elif salary < 3082:
        cardinal = 3082
    else:
        cardinal = salary
    if isLeast:
        cardinal = 3082
    return cardinal * 0.002


def injury(salary, isLeast):
    if salary > 23118:
        cardinal = 23118
    elif salary < 4624:
        cardinal = 4624
    else:
        cardinal = salary
    if isLeast:
        cardinal = 4624
    return cardinal * 0


def maternity(salary, isLeast):
    if salary > 23118:
        cardinal = 23118
    elif salary < 4624:
        cardinal = 4624
    else:
        cardinal = salary
    if isLeast:
        cardinal = 4624
    return cardinal * 0


def house(salary):
    if salary > 23118:
        cardinal = 23118
    else:
        cardinal = salary
    return cardinal * 0.12


def tax(salary):
    tax = 0
    if salary > 3500:
        s1 = salary - 3500
    if s1 > 80000:
        tax += (s1 - 80000) * 0.45
        s1 = 80000
    if s1 > 55000:
        tax += (s1 - 55000) * 0.35
        s1 = 55000
    if s1 > 35000:
        tax += (s1 - 35000) * 0.3
        s1 = 35000
    if s1 > 9000:
        tax += (s1 - 9000) * 0.25
        s1 = 9000
    if s1 > 4500:
        tax += (s1 - 4500) * 0.2
        s1 = 4500
    if s1 > 1500:
        tax += (s1 - 1500) * 0.1
        s1 = 1500
    if s1 > 0:
        tax += s1 * 0.03
    return tax


if __name__ == "__main__":
    print("Please input your Pre-Tax salary:")
    salary = float(input())
    print("Soucial Insurance At the lowest limit?(Y/N)")
    limit = str(input()).lower()
    isLimit = limit == "y"
    salary_house = house(salary)
    salary_endow = endowment(salary, isLimit)
    salary_medical = medical(salary, isLimit)
    salary_unemploy = unemployment(salary, isLimit)
    salary_injury = injury(salary, isLimit)
    salary_maternity = maternity(salary, isLimit)
    taxed_salary = salary - salary_house - salary_endow - salary_medical - salary_unemploy - salary_injury - salary_maternity
    salary_tax = tax(taxed_salary)
    payed = taxed_salary - salary_tax
    print("Your After-Tax salary is:")
    print(payed)

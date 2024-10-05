from sympy import symbols, Eq, latex
from sympy.parsing.sympy_parser import parse_expr
from re import findall, sub
from string import ascii_lowercase as var_names
from functools import wraps


def latex_wrap(func):
	# Оборачиваю в $
    @wraps(func)
    def wrapper(*args, **kwargs):
        return f'${func(*args, **kwargs)}$'
    return wrapper


def number(func):
	# Добавляю номер формулы
    @wraps(func)
    def wrapper(*args, **kwargs):
        num_f = input("Введите номер формулы: ")
        print("Введите данные:")
        return r'\begin{equation}' + f' {func(*args, **kwargs)}' + r' \tag{' + num_f + '} ' + r'\end{equation}'

    return wrapper


def index(func):
    # Создаю многосимвольные индексы
    @wraps(func)
    def wrapper(*args, **kwargs):
        def sub_index(m):
            pattern = (m[1] == '_') and r'_\1{}' or r'^\1{}'
            return sub(r'([\w()])', pattern, m[2])

        pattern = r'(_)(\w+)'
        res = sub(pattern, sub_index, func(*args, **kwargs))
        pattern = r'(\^)((?:[^_\W]|[()])+)'
        res = sub(pattern, sub_index, res)
        return res.replace('__', r'_\_')
    return wrapper



def convert_name(func):
	# Даю временные имена переменным
    # После преобразования возвращаю имена
    @wraps(func)
    def wrapper(*args, **kwargs):
        pattern = r"\\[\w.,]+(?:\{[\w.,]+\})+|(?:\\[\w.,]+)+|[\w^.,]+"
        expr = input()
        old_var = findall(pattern, expr)
        print(old_var)
        dict_names = {(k * 3): v for k, v in zip(var_names, old_var)}
        for k, v in dict_names.items():
            expr = expr.replace(v, k)
        res = func(expr)
        for k, v in dict_names.items():
            res  = res.replace(k, v)
        return res
    return wrapper


@latex_wrap
@number
@index
@convert_name
def convert_to_latex(expr_str):
    # Разбиваем строку на левую и правую часть уравнения
    lhs, rhs = expr_str.split("=")
    # Парсим левую и правую часть
    lhs_expr = parse_expr(lhs.strip())
    rhs_expr = parse_expr(rhs.strip())
    # Создаем уравнение
    equation = Eq(lhs_expr, rhs_expr)
    # Возвращаем его в виде строки LaTeX с символом умножения '\cdot'
    return latex(equation, mul_symbol=" \\cdot ").replace('\\frac', '\\dfrac')


print(convert_to_latex())

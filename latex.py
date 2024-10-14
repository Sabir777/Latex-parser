from sympy import symbols, Eq, latex
from sympy.parsing.sympy_parser import parse_expr
from re import findall, sub, split, escape
from itertools import permutations
from functools import wraps
from string import ascii_lowercase


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


def cdot(func):
	# Меняю *(звездочку) на \cdot
    @wraps(func)
    def wrapper(*args, **kwargs):
        pattern = r'\s*\*\s*'
        return sub(pattern, ' \\\cdot ', func(*args, **kwargs))
    return wrapper


def index(func):
    # Создаю многосимвольные индексы
    @wraps(func)
    def wrapper(*args, **kwargs):
        def sub_index(m):
            pattern = (m[1] == '_') and r'_\1{}' or r'^\1{}'
            return sub(r'([-\w()])', pattern, m[2])

        pattern = r'(_)([-\w]+)'
        res = sub(pattern, sub_index, func(*args, **kwargs))
        pattern = r'(\^)((?:[^_\W]|[()])+)'
        res = sub(pattern, sub_index, res)
        return res.replace('__', r'_\_')
    return wrapper

def not_equal(func):
    # Разбиваю неравенство на части
    # Обрабатываю каждую часть отдельно
    # Соединяю обработанные части

    @wraps(func)
    def wrapper(*args, **kwargs):
        expression = input()
        pattern = r'\\approx|\\geq|\\leq|<|>'
        lst_del = findall(pattern, expression)
        lst_expr = split(pattern, expression)
        if not lst_del:
            return func(expression)

        it_expr = iter(lst_expr)
        res = func(next(it_expr)).strip()
        for d in lst_del:
            res += f' {d} {func(next(it_expr)).strip()}'
        return res

    return wrapper


def fake_eq(func):
    # Добавляю левую часть уравнения
    # если ее нет;
    # Если выражение длинное,
    # то разбиваю его на парные части
    # обрабатываю их как уравнения
    # и потом все соединяю вместе
    # фейковую часть убираю;

    @wraps(func)
    def wrapper(expr):
        lst_expr = expr.split("=")
        size = len(lst_expr)
        if size % 2:
            lst_expr = ['fake'] + lst_expr
        res_exprs = []
        for i in range(0, size, 2):
            lhs, rhs = lst_expr[i], lst_expr[i + 1]
            res = func(f'{lhs} = {rhs}')
            if res.find('fake') != -1:
                res = res.split("=")[1].lstrip()
            res_exprs.append(res)
        return ' = '.join(res_exprs)

    return wrapper


def convert_name(first, pattern):
    def decorator(func):
        # Даю временные имена переменным
        # После преобразования возвращаю имена
        @wraps(func)
        def wrapper(expr):
            # итератор имен переменных
            it_num = permutations(ascii_lowercase[first: first+8])
            # Заменяю все символы latex на временные переменные
            old_var = findall(pattern, expr)
            # print(old_var)
            dict_names = {''.join(k): v for k, v in zip(it_num, old_var)}
            for k, v in dict_names.items():
                pattern2 = (v[0] != '\\' and v[-1] != '}') and r'(?<![.,])\b' + escape(v) + r'\b(?![.,])' or escape(v)
                expr = sub(pattern2, k, expr)
            # print('вывод\n',expr)
            res = func(expr)
            for k, v in dict_names.items():
                res  = res.replace(k, v)
            return res
        return wrapper
    return decorator


@latex_wrap
@latex_wrap
# @number # добавить номер формулы справа
@cdot
@index
@not_equal
@fake_eq
@convert_name(0, r'\\\w+(?:\{.+?\})?') # \sqrt{3}
@convert_name(1, r'\b\w+\{\w+\}') # I_{abcdefgh}
@convert_name(2, r'\b[-\w^().,]+\b') # I^(3)_кз abcdefghbcdefghi
def convert_to_latex(expr_str):
    '''Конвертор математических выражений в LaTeX-выражения'''
    # Разбиваем строку на левую и правую часть уравнения
    lhs, rhs = expr_str.split("=")
    # Парсим левую и правую часть
    lhs_expr = parse_expr(lhs.strip())
    rhs_expr = parse_expr(rhs.strip())
    # Создаем уравнение
    equation = Eq(lhs_expr, rhs_expr)
    # Возвращаем его в виде строки LaTeX с символом умножения '\cdot'
    return latex(equation, mul_symbol=" \\cdot ").replace('\\frac', '\\dfrac')


try:
    print(convert_to_latex())
except:
    print("Ошибка в выражении")

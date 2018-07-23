# Документация - http://www.dabeaz.com/ply/ply.html

import ply.lex as lex
import ply.yacc as yacc
import sys

# Список с названиями токенов
tokens = [

    'INT',
    'FLOAT',
    'NAME',
    'PLUS',
    'MINUS',
    'DIVIDE',
    'MULTIPLY',
    'EQUALS'

]

# Регулярные выражения, которые описывают что находится в токенах
t_PLUS = r'\+'
t_MINUS = r'\-'
t_MULTIPLY = r'\*'
t_DIVIDE = r'\/'
t_EQUALS = r'\='

# Ply's special t_ignore variable allows us to define characters the lexer will ignore.Специальная переменная t_ignore позволяет указать символы, которые будет игнорировать lex
# Игнорим только пробелы, так как в перспективе будем работать с переменными.
t_ignore = r' '

# Описание сложных токенов, чья длинна может быть более одного символа.
# указаны через функции.
# Флот на первом месте, чтобы питон распознавал его первым, иначе могут быть неточности если мы сперва будет делать инт.
def t_FLOAT(t):
    r'\d+\.\d+'  # число с любым кол-вом знаков до разделителя точка, точка, любое число знаков после точки.
    t.value = float(t.value) #Лексема, сравнение текста.
    return t

# Инт может быть более чем один символ.
def t_INT(t):
    r'\d+'
    t.value = int(t.value)
    return t

# NAME - это имя кастомной переменной. Может быть 1 или более символов в длинну.
# Первый символ должен быть в промежутке от a-z или нижнее подчеркивание, остальные символы могут быть тоже буквами или нижним подчеркиванием или цифрой.
def t_NAME(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = 'NAME'
    return t

# Пропустить этот токен, чтобы не было ошибки и выдать сообщениеиспользуя специальную функцию Плай t_error.
def t_error(t):
    print("Неверное значение")
    t.lexer.skip(1)

# Создаем lexer.
lexer = lex.lex()

# Это специальная магия Ply для того чтобы указать парсеру в каком порядке нужно делать вычисления. Скопировано от сюда - https://www.dabeaz.com/ply/example.html
precedence = (

    ('left', 'PLUS', 'MINUS'),
    ('left', 'MULTIPLY', 'DIVIDE')

)

# Указываем грамматику согласно пункту 6.2 дока. Разрешаем expressions, var_assign и empty.
def p_calc(p):
    '''
    calc : expression
         | var_assign
         | empty
    '''
    print(run(p[1]))

def p_var_assign(p):
    '''
    var_assign : NAME EQUALS expression
    '''
    # Создается дерево парсера
    p[0] = ('=', p[1], p[3])

# Правила выражений.
def p_expression(p):
    '''
    expression : expression MULTIPLY expression
               | expression DIVIDE expression
               | expression PLUS expression
               | expression MINUS expression
    '''
    # Сощдается дерево парсера.
    p[0] = (p[2], p[1], p[3])

def p_expression_int_float(p):
    '''
    expression : INT
               | FLOAT
    '''
    p[0] = p[1]

def p_expression_var(p):
    '''
    expression : NAME
    '''
    p[0] = ('var', p[1])

# Все что не expressions, var_assign и empty - это ошибка.
# p_error - это еще одна магия Ply.
def p_error(p):
    print("Синтаксическая ошибка.")

def p_empty(p):
    '''
    empty :
    '''
    p[0] = None

# Делаем парсер
parser = yacc.yacc()

# Словарь для хранения и извлечения переменных.
env = {}

# Эту функция проходит по сгенерированному парсером дереву.
def run(p):
    global env
    if type(p) == tuple:
        if p[0] == '+':
            return run(p[1]) + run(p[2])
        elif p[0] == '-':
            return run(p[1]) - run(p[2])
        elif p[0] == '*':
            return run(p[1]) * run(p[2])
        elif p[0] == '/': 
            return run(p[1]) / run(p[2])
        elif p[0] == '=':
            env[p[1]] = run(p[2])
            return ''
        elif p[0] == 'var':
            if p[1] not in env:
                return 'Undeclared variable found!'
            else:
                return env[p[1]]
    else:
        return p

# Создаем интерфейс для взаимодействия с калькулятором. 
while True: 
    try:
        s = input('Введите выражение: ')
    except EOFError:
        break 
    parser.parse(s)
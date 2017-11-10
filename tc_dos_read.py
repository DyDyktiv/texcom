from re import compile as load
import tc_classes
import tc_analize

criteria = ('* Ключ таблицы',
            '* Заголовок таблицы',
            '* Формат таблицы',
            '* Тело таблицы')
re_doc_test = load('''[a-zA-Z0-9а-яА-Я* \n_,.?!+-/\\\|^=<>\(\)'";:$%&@]+''')
re_attr_str = load('[A-Z]+\.[A-Z0-9]+=X\([0-9]+\)".*"')
re_attr_num = load('[A-Z]+\.[A-Z0-9]+=9*[V|,|\.]?9*(?[0-9]*)?".*"')
re_attr_name = load('[A-Z]+\.[A-Z0-9]+')
re_attr_str_long = load('=X\(\d+\)"')
re_attr_num_long = load('=9*[V|,|\.]?9*"')
rereal = load('[9]+[V,\.][9]+')


def isfloat(value):
    try:
        float(value)
        return True
    except ValueError:
        return False


def attrwork(input_string):
    """Преобразует строку атрибутов в массив аттрибутов"""
    attrs = list(filter(lambda x: x, input_string.split(';')))  # Разбиение строки атрибутов на список атрибутов
    errors = []  # Список ошибок
    for i, c in enumerate(attrs):
        if re_attr_str.match(c):
            attrs[i] = tc_classes.Attr(re_attr_name.match(c).group(), c.split('"')[1], 'str',
                                       int(re_attr_str_long.search(c).group()[3:-2]))
        elif re_attr_num.match(c):
            long = re_attr_num_long.search(c).group()[1: -1]
            attrs[i] = tc_classes.Attr(re_attr_name.match(c).group(), c.split('"')[1],
                                       ['int', 'float']['V' in long], len(long))
        else:
            errors.append(c)
    if errors:
        return 3, errors
    elif attrs:
        return 0, attrs
    else:
        return 6, input_string

def recordwork(s, attrs):
    """Преобразует строку в запись по макету атрибутов"""
    record = []
    copy = s
    errors = []

    for attr in attrs:
        if s:
            k = s[: attr.long].strip()
            if attr.mode == 'float':
                k = k.replace(',', '.')
                if isfloat(k):
                    record.append(float(k))
                elif k == '.' or k == '':
                    record.append(0.0)
                else:
                    errors.append([copy, k, 'float'])
                    continue
            elif attr.mode == 'int':
                if k.isdigit():
                    record.append(int(k))
                elif k == '':
                    record.append(0)
                else:
                    errors.append([copy, k, 'int'])
                    continue
            else:
                record.append(k)
            s = s[attr.long:]
        else:
            if attr.mode == 'int' or attr.mode == 'float':
                record.append(0)
            else:
                record.append('')
    if errors:
        return [5, errors]
    else:
        return 0, record

def dosindata(inputdata):
    """Анализирует dos файл и возвращает находящиеся в нем данные"""

    # Создание объекта файла
    d = tc_classes.Document
    d.dos_name = inputdata.name

    # Чтение "таблицы"
    f = open(inputdata.pathing(), encoding='cp866')
    t = f.read()
    f.close()

    # Проверка на кодировку
    if '* Ключ таблицы' != t[0: 14]:
        t = t.encode('cp866').decode('cp1251')
        if '* Ключ таблицы' != t[0: 14]:
            return [1]

    # Проверка на наличие неопознанных символов, т.е. битый ли файл
    if re_doc_test.match(t).span() != (0, len(t)):
        problems = []
        for char in t:
            if not re_doc_test.match(char):
                if char not in problems:
                    problems.append(char)
        return [2, problems]

    # Преобразование файла в список строк
    t = t.split('\n')

    # Удаление комментариев и конечных пробелов
    for i in range(len(t)):
        if t[i].count('//'):
            t[i] = t[i][: t[i].find('//')]
        t[i] = t[i].rstrip()

    # Удаление пустых строчек
    t = list(filter(lambda x: x, t))

    # Выделение имени файла
    while criteria[0] != t[0] and len(t):
        del (t[0])
    if len(t) < 7:
        return [4]
    del (t[0])
    d.name = t[0]
    del (t[0])

    # Выделение заголовка таблицы
    while criteria[1] != t[0] and len(t):
        del (t[0])
    if len(t) < 5:
        return [4]
    del (t[0])
    d.note = []
    while t[0][0] != '*':
        d.note.append(t[0])
        del (t[0])
    d.note = ' '.join(d.note)

    # Выделение атрибутов таблицы
    while criteria[2] != t[0] and len(t):
        del (t[0])
    if len(t) < 3:
        return [4]
    del (t[0])
    attrs = attrwork(t[0])
    del (t[0])
    if attrs[0] == 0:
        d.atrs = attrs[1]
    else:
        return attrs

    # Вычленение записей
    while criteria[3] != t[0] and len(t):
        del (t[0])
    if len(t) == 0:
        return [4]
    del (t[0])
    records = []
    while len(t):
        record = recordwork(t[0], d.atrs)
        if record[0] == 0:
            records.append(record[1])
            d.recs.append(record[1])
        else:
            return record
        del (t[0])

    return d



f = dosindata(r)

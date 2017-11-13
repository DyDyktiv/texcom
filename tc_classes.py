import os.path
import re


re_doc_test = re.compile('''[a-zA-Z0-9а-яА-Я* \n_,.?!+\-/\\\|^=<>'";:$%&@()]+''')
re_attr_str = re.compile('[A-Z]+\.[A-Z0-9]+=X\([0-9]+\)".*"')
re_attr_num = re.compile('[A-Z]+\.[A-Z0-9]+=9*[V,.]?9*\(?[0-9]*\)?".*"')
re_attr_name = re.compile('[A-Z]+\.[A-Z0-9]+')
re_attr_str_long = re.compile('=X\(\d+\)"')
re_attr_num_long = re.compile('=9*[V,.]?9*"')
real = re.compile('\d+[,.]?\d+')


class EError:
    def __init__(self, name, note=None):
        self.name = name
        self.note = note

    def print(self):
        print(self.name)
        print(self.note)


class Attr:
    def __init__(self, name, mask, mode, long=0):
        self.name = name
        self.mask = mask
        self.mode = mode
        self.long = long


class Document:
    def __init__(self, name, path, mode):
        self.error = False
        self.dos_name = None
        self.name = None
        self.path = path
        self.size = 0
        self.note = None
        self.atrs = []
        self.recs = []

        if mode == 'dos':
            self.dos_name = name
            self.fdossize()
        elif mode == 'xml':
            self.name = name[:name.rfind('.')]
            self.fxmlsize()
        elif mode == 'MDB':
            self.name = name[:name.rfind('.')]
            self.fmdbsize()

    def fdossize(self):
        self.size = os.path.getsize(os.path.join(self.path, self.dos_name))

    def fxmlsize(self):
        self.size = os.path.getsize(os.path.join(self.path, self.name + '.xml'))

    def fmdbsize(self):
        self.size = os.path.getsize(os.path.join(self.path, self.name + '.json'))

    def dos_read(self):
        f = open(os.path.join(self.path, self.dos_name), encoding='cp866')
        t = f.read()
        f.close()

        # Проверка на кодировку
        if '* Ключ таблицы' != t[0: 14]:
            t = t.encode('cp866').decode('cp1251')
            if '* Ключ таблицы' != t[0: 14]:
                self.error = EError('Ошибка кодировки')
                return False

        # Проверка на наличие неопознанных символов, т.е. битый ли файл
        if re_doc_test.match(t).span() != (0, len(t)):
            problems = []
            for char in t:
                if not re_doc_test.match(char):
                    if char not in problems:
                        problems.append(char)
            self.error = EError('Неопознанные символы', problems)
            return False

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
        while '* Ключ таблицы' != t[0] and len(t):
            del (t[0])
        if len(t) < 7:
            self.error = EError('Несоответствие стурктуры файла: отсутствует "* Ключ таблицы"')
            return False
        del (t[0])
        self.name = t[0]
        del (t[0])

        # Выделение заголовка таблицы
        while '* Заголовок таблицы' != t[0] and len(t):
            del (t[0])
        if len(t) < 5:
            self.error = EError('Несоответствие стурктуры файла: отсутствует "* Заголовок таблицы"')
            return False
        del (t[0])
        self.note = []
        while t[0][0] != '*':
            self.note.append(t[0])
            del (t[0])
        self.note = ' '.join(self.note)

        # Выделение атрибутов таблицы
        while '* Формат таблицы' != t[0] and len(t):
            del (t[0])
        if len(t) < 3:
            self.error = EError('Несоответствие стурктуры файла: отсутствует "* Формат таблицы"')
            return False
        del (t[0])
        report = dosattrwork(t[0])
        del (t[0])
        if report[0]:
            self.atrs = report[1]
        else:
            self.error = report[1]
            return False

        # Вычленение записей
        while '* Тело таблицы' != t[0] and len(t):
            del (t[0])
        if len(t) == 0:
            self.error = EError('Несоответствие стурктуры файла: отсутствует "* Тело таблицы"')
            return False
        del (t[0])
        while len(t):
            report = dosrecordwork(t[0], self.atrs)
            if report[0]:
                self.recs = report[1]
            else:
                self.error = report[1]
                return False
            del (t[0])


def dosattrwork(s):
    """Преобразует строку атрибутов в массив аттрибутов"""
    atrs = list(filter(lambda x: x, s.split(';')))
    errors = []  # Список ошибок
    for i, c in enumerate(atrs):
        if re_attr_str.match(c):
            atrs[i] = Attr(re_attr_name.match(c).group(), c.split('"')[1], 'str',
                           int(re_attr_str_long.search(c).group()[3:-2]))
        elif re_attr_num.match(c):
            long = re_attr_num_long.search(c).group()[1: -1]
            atrs[i] = Attr(re_attr_name.match(c).group(), c.split('"')[1],
                           ['int', 'float']['V' in long], len(long))
        else:
            errors.append(c)
    if errors:
        return False, EError('Непонятный аттрибут', errors)
    elif atrs:
        return True, atrs
    else:
        return False, EError('Аттрибуты не обнаружены', s)


def dosrecordwork(s: str, atrs):
    """Преобразует строку в запись по макету атрибутов"""
    rept = []
    errors = []  # Список ошибок
    for a in atrs:
        if s:
            n = a.long
            if len(s) > n:
                w = s[:n]
                s = s[n:]
            else:
                w = s
                s = False
            w.strip()
            if a.mode == 'str':
                rept.append(w)
            elif a.mode == 'int':
                if w.isdigit():
                    rept.append(int(w))
                else:
                    errors.append(('to int:', w))
            elif a.mode == 'float':
                w.replace(',', '.')
                w.replace('V', '.')
                if w.isdecimal():
                    rept.append(float(w))
                else:
                    errors.append(('to float:', w))
        else:
            rept.append(None)
    if errors:
        return False, EError('Ошибка чтения', errors)
    elif rept:
        return True, rept

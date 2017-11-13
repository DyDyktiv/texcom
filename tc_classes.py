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
                self.recs.append(report[1])
            else:
                self.error = report[1]
                return False
            del (t[0])

    def xml_read(self):
        f = open(os.path.join(self.path, self.name + '.xml'), encoding='utf-8')
        if f.readline() == '<?xml version="1.0" encoding="UTF-8"?>\n':
            s = f.readline()
            self.dos_name = s[s.find('dos_name="') + 10: s.find('" note=')]
            self.note = s[s.find('note="') + 6: s.find('">')]

            f.readline()
            while True:
                s = f.readline()
                if '</attrs>' in s:
                    break
                self.atrs.append(Attr(s[s.find('name="') + 6: s.find('" mask')],
                                      s[s.find('mask="') + 6: s.find('" type')],
                                      s[s.find('type="') + 6: -4]))

            f.readline()
            while True:
                s = f.readline()
                if '</records>' in s:
                    break
                s = list(map(lambda x: x[x.find('"') + 1: x.rfind('"')], re.split('fild\d', s)[1:]))
                for i, a in enumerate(self.atrs):
                    if a.mode == 'int':
                        s[i] = int(s[i])
                    elif a.mode == 'float':
                        s[i] = float(s[i])
                self.recs.append(s)

        else:
            self.error = EError('Ошибка чтения')
            return False
        f.close()

    def mdb_read(self):
        f = open(os.path.join(self.path, self.name + '.json'), encoding='utf-8')
        f.readline()
        s = f.readline()
        self.dos_name = s[s.find('"dos name": "') + 13: s.rfind('"')]
        s = f.readline()
        self.note = s[s.find('"note": "') + 9: s.rfind('"')]
        f.readline()
        while True:
            s = f.readline()
            if '    ],\n' == s:
                break
            if '        "attr": {\n' == s:
                s = f.readline()
                name = s[s.find('"name": "') + 9: s.rfind('"')]
                s = f.readline()
                mask = s[s.find('"mask": "') + 9: s.rfind('"')]
                s = f.readline()
                mode = s[s.find('"type": "') + 9: s.rfind('"')]
                self.atrs.append(Attr(name, mask, mode))
        f.readline()
        while True:
            s = f.readline()
            if '    ]' in s:
                break
            elif '        "record": {\n' == s:
                record = []
                for a in self.atrs:
                    s = f.readline()
                    if a.mode == 'str':
                        record.append(s[s.find('": "') + 4: s.rfind('"')])
                    elif a.mode in ('int', 'float'):
                        if 'None' in s:
                            record.append(None)
                        else:
                            record.append(real.search(s).group())
                self.recs.append(record)
        f.close()

    def xml_save(self, path):
        t = ' ' * 4
        f = open(os.path.join(path, self.name + '.xml'), 'w', encoding='utf-8')
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<data dos_name="{}" note="{}">\n'.format(self.dos_name, self.note))

        f.write(2 * t + '<attrs>\n')
        for a in self.atrs:
            f.write(3 * t + '<attr name="{}" mask="{}" type="{}"/>\n'.format(a.name, a.mask, a.mode))
        f.write(2 * t + '</attrs>\n')

        f.write(2 * t + '<records>\n')
        for record in self.recs:
            s = 3 * t + '<record '
            for i, word in enumerate(record):
                s += 'fild{}="{}" '.format(i, word)
            s += '/>\n'
            f.write(s)
        f.write(2 * t + '</records>\n')
        f.write('</data>\n')
        f.close()

    def mdb_save(self, path):
        t = ' ' * 4
        f = open(os.path.join(path, self.name + '.json'), 'w', encoding='utf-8')
        f.write('{\n')
        f.write(t + '"dos name": "{}",\n'.format(self.dos_name))
        f.write(t + '"note": "{}",\n'.format(self.note))
        f.write(t + '"attrs": [\n')
        collector = []
        for a in self.atrs:
            s = 2 * t + '"attr": {\n'
            s += 3 * t + '"name": "{}",\n'.format(a.name)
            s += 3 * t + '"mask": "{}",\n'.format(a.mask)
            s += 3 * t + '"type": "{}"\n'.format(a.mode)
            collector.append(s)
        s = 2 * t + '},\n'
        f.write(s.join(collector))
        f.write(2 * t + '}\n')
        f.write(t + '],\n')

        f.write(t + '"records": [\n')
        collector = []
        for record in self.recs:
            s = []
            for i, a in enumerate(self.atrs):
                if a.mode in ('int', 'float'):
                    s.append(t * 3 + '"fild{}": {}'.format(i, record[i]))
                else:
                    s.append(t * 3 + '"fild{}": "{}"'.format(i, record[i]))
            s = t * 2 + '"record": {\n' + ',\n'.join(s) + '\n'
            collector.append(s)
        s = t * 2 + '},\n'
        f.write(s.join(collector))
        f.write(2 * t + '}\n')
        f.write(t + ']\n')
        f.write('}\n')
        f.close()

    def print(self):
        print('Erorr?...{}'.format((False, True)[self.error]))
        print('Name: {}     dos name: {}     size: {} B'.format(self.name, self.dos_name, self.size))
        print('Path: {}'.format(self.path))
        print('Note: {}'.format(self.note))
        print('Attrs:')
        for a in self.atrs:
            print('-Name: {}   Type: {}   Mask: {}'.format(a.name, a.mode, a.mask))
        print('Records:')
        for r in self.recs:
            print('-{}'.format(r))


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
            w = w.strip()
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

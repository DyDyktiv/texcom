from os import chdir, listdir, mkdir
from os.path import isfile, isdir
from time import strftime
import tc_dos_read


errorcode = ('',
             'Неопознанная кодировка',
             'Неопознанные символы',
             'Непонятный атрибут таблицы',
             'Несоответствие структуры файла',
             'Ошибка типа поля файла',
             'Отсутствие атрибутов таблицы')


def datainxml(ref, name, note, attrs, records):
    """Сохраняет полученные данные в xml формате"""
    return name
    t = 2 * ' '

    f = open(ref + '/' + name + '.xml', 'w', encoding='utf-8')
    f.write('<base>\n')
    f.write(t + '<note>' + note + '</note>\n')
    f.write(t + '<attrs>\n')
    for attr in attrs:
        f.write(2 * t + '<attr>\n')
        f.write(3 * t + '<name>' + attr[0] + '</name>\n')
        f.write(3 * t + '<mask>' + attr[1] + '</mask>\n')
        f.write(3 * t + '<type>' + attr[2] + '</type>\n')
        f.write(2 * t + '</attr>\n')
    f.write(t + '</attrs>\n')
    f.write(t + '<records>\n')
    for record in records:
        f.write(2 * t + '<record>\n')
        for i, field in enumerate(record):
            f.write(3 * t + '<field' + str(i) + '>' +
                    str(field) +
                    '</field' + str(i) + '>\n')
        f.write(2 * t + '</record>\n')
    f.write(t + '</records>\n')
    f.write('</base>')
    f.close()
    return name

def search(refdos, refxml, zero=False):
    """Поиск файлов базы знаний по адрессу ref вглубь"""

    if zero:
        refxml += 'BASE ' + str(zero)
    mkdir(refxml)

    # Получаем список файлов и папок в директории
    chdir(refdos)
    m = listdir()

    # Список файлов для текущего анализа
    mf = list(filter(lambda x: isfile(x), m))

    # Список папок для дальнейшего анализа
    md = list(filter(lambda x: isdir(x), m))

    del m

    # Выборка файлов с расширениями, состоящих из цифр
    mf = list(filter(lambda x: x[x.rfind('.') + 1:].isdigit(), mf))

    # Общее количество обработанных файлов и количество успешно обработанных
    s = [0, 0]

    # Обработка файлов в текущей директории
    path = refdos[refdos.rfind('BASE') + 4:] + '/'
    for c in mf:
        m = tc_dos_read.dosindata(refdos + '/' + c)
        s[0] += 1
        if m[0] == 0:
            m = datainxml(refxml, m[1], m[2], m[3], m[4])
            s[1] += 1
        else:
            print(path + c, ' ' + errorcode[m[0]] + ':', end=' ')
            if m[0] == 2:
                print('"', end='')
                for i in m[1]:
                    print(i, end='')
                print('"')
            elif m[0] == 5:
                print()
                for i in m[1]:
                    print(i)
            else:
                print('\n' + m[1:])
    del mf

    # Обход вложенных дирректорий
    for c in md:
        m = search(refdos + '/' + c, refxml + '/' + c)
        s[0] += m[0]
        s[1] += m[1]
        chdir(refdos)
    return s

def starting():
    refdos = input('Введите расположение папки BASE:\n')
    if refdos[-4:] == 'BASE':
        refdos += '/'
    elif refdos[-5: -1] == 'BASE':
        pass
    elif refdos[-1] in ['/', '\\']:
        refdos += 'BASE/'
    else:
        refdos += '/BASE/'
    refxml = refdos[: -5]
    new_base = strftime('%H.%M.%S %d.%m.%Y')
    s = search(refdos, refxml, new_base)
    print('Количество обработанных файлов: ' + str(s[0]),
          '\n' + 'Количество успешно преобразованных файлов: ' + str(s[1]),
          '\nРезультат работы программы находится в папке BASE ' + new_base)


starting()

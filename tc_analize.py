import os
import os.path
import re


class File:
    def __init__(self, name, path):
        self.name = name
        self.path = path
        self.size = os.path.getsize(os.path.join(path, name))

def analize(dbpath, dbtype):
    if dbtype == 'dos':
        dbtype = re.compile('\.[\d]{3}')
    elif dbtype == 'xml':
        dbtype = re.compile('\.xml')
    elif dbtype == 'MDB':
        dbtype == re.compile('\.json')

    fullsize = 0

    objs = os.listdir(dbpath)
    dirs = list(filter(lambda x: os.path.isdir(os.path.join(dbpath, x)), objs))
    files = list(map(lambda f: File(f, dbpath), filter(lambda x: dbtype.search(x), objs)))

    for d in dirs:
        objs = os.listdir(os.path.join(dbpath, d))
        dirs.extend(map(lambda xx: os.path.join(d, xx),
                        filter(lambda x: os.path.isdir(os.path.join(dbpath, d, x)), objs)))
        #files.extend(map(lambda f:, filter(lambda x: dbtype.search(x), objs)))

    print(len(dirs))
    print(dirs)
    print(len(objs))


analize('D:/YandexDisk/Документы/6 семестр/СБД/texkom/BASE', 'dos')

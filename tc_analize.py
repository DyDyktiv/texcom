import os
import os.path
import re


class File:
    def __init__(self, name, path):
        self.name = name
        self.path = path
        self.size = os.path.getsize(os.path.join(path, name))


    def pathing(self):
        return os.path.join(self.path, self.name)


class Report:
    def __init__(self):
        self.fullsize = 0
        self.files = []


def analize(dbpath, dbtype):
    if dbtype == 'dos':
        mask = re.compile('\.[\d]{3}')
    elif dbtype == 'xml':
        mask = re.compile('\.xml')
    elif dbtype == 'MDB':
        mask = re.compile('\.json')

    objs = os.listdir(dbpath)
    dirs = list(filter(lambda x: os.path.isdir(os.path.join(dbpath, x)), objs))
    files = list(map(lambda f: File(f, dbpath), filter(lambda x: mask.search(x), objs)))

    for d in dirs:
        objs = os.listdir(os.path.join(dbpath, d))
        dirs.extend(map(lambda xx: os.path.join(d, xx),
                        filter(lambda x: os.path.isdir(os.path.join(dbpath, d, x)), objs)))
        files.extend(map(lambda f: File(f, os.path.join(dbpath, d)), filter(lambda x: mask.search(x), objs)))

    r = Report
    r.fullsize = sum(map(lambda x: x.size, files))
    r.files = files

    return r

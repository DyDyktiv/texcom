import os
import os.path
import re
import tc_classes


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
    files = list(map(lambda f: tc_classes.Document(f, dbpath, dbtype), filter(lambda x: mask.search(x), objs)))

    for d in dirs:
        objs = os.listdir(os.path.join(dbpath, d))
        dirs.extend(map(lambda xx: os.path.join(d, xx),
                        filter(lambda x: os.path.isdir(os.path.join(dbpath, d, x)), objs)))
        files.extend(map(lambda f: tc_classes.Document(f, os.path.join(dbpath, d), dbtype),
                         filter(lambda x: mask.search(x), objs)))

    r = Report
    r.fullsize = sum(map(lambda x: x.size, files))
    r.files = files

    return r

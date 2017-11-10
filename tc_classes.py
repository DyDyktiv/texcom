import os.path


class Attr:
    def __init__(self, name, mask, mode, long=0):
        self.name = name
        self.mask = mask
        self.mode = mode
        self.long = long


class Document:
    def __init__(self, name, path, mode):
        self.errors = False
        self.dos_name = False
        self.name = False
        self.path = path
        self.size = 0

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


r = Document('FPRR.001', 'D:/YandexDisk/Документы/6 семестр/СБД/texkom/BASE', 'dos')
r.dos_read()



import os.path


class Attr:
    def __init__(self, name, mask, mode, long=0):
        self.name = name
        self.mask = mask
        self.mode = mode
        self.long = long


class Document:
    def __init__(self, name, path, mode):
        self.dos_name = False
        self.xml_name = False
        self.mdb_name = False
        self.dos_path = False
        self.xml_path = False
        self.mdb_path = False
        self.dos_size = 0
        self.xml_size = 0
        self.mdb_size = 0

        if mode == 'dos':
            self.dos_name = name
            self.dos_path = path
            self.fdossize()
        elif mode == 'xml':
            self.xml_name = name
            self.xml_path = path
            self.fxmlsize()
        elif mode == 'MDB':
            self.mdb_name = name
            self.mdb_path = path
            self.fmdbsize()

    def fdossize(self):
        self.dos_size = os.path.getsize(os.path.join(self.dos_path, self.dos_name))

    def fxmlsize(self):
        self.xml_size = os.path.getsize(os.path.join(self.xml_path, self.xml_name + '.xml'))

    def fmdbsize(self):
        self.mdb_size = os.path.getsize(os.path.join(self.mdb_path, self.mdb_name + '.json'))

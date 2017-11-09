class Attr:
    def __init__(self, name, mask, mode, long=0):
        self.name = name
        self.mask = mask
        self.mode = mode
        self.long = long


class Document:
    def __init__(self):
        self.dos_name = False
        self.name = ''
        self.note = ''
        self.atrs = False
        self.recs = False

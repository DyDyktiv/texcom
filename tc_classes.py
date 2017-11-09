class Attr:
    def __init__(self, name, mask, mode, long=0):
        self.name = name
        self.mask = mask
        self.mode = mode
        self.long = long


class Document:
    def __init__(self):
        self.dos_name = ''
        self.name = ''

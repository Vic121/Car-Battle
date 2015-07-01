# TODO: use ekg

class Gg(object):
    """obsluga wysylania wiadomosci przez gg"""

    def __init__(self):
        self.my_uin = 0
        self.my_password = ''

    def message(self, uin, msg):
        pass


if __name__ == '__main__':
    g = Gg()
    g.message(413919, 'sth')

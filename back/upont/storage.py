from storages.backends.ftp import FTPStorage

from .settings import STATIC_URL


class StaticStorage(FTPStorage):
    def url(self, name):
        return STATIC_URL + name

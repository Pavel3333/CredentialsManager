from src.Constants import Constants
from os.path import exists, getmtime, getsize, join
from time import gmtime, strftime


class Credentials(object):
    _TIME_FMT = '%d %b %Y %H:%M:%S'
    _TIME_OFFSET = 3 * 60 * 60  # UTC+3 time offset
    _SIZES = ('B', 'KB', 'MB')

    __slots__ = ('__id', '__name', '__path', '__modify_time', '__size')

    def __init__(self, id_):
        super(Credentials, self).__init__()

        self.__id = id_
        self.__name = name = Constants.CredentialsNameFmt.format(id_)
        self.__path = join(Constants.CredentialsDir, name)
        self.__modify_time = None
        self.__size = None

        self.update()

    def update(self):
        if self.is_exists():
            path = self.__path

            self.__modify_time = getmtime(path)
            self.__size = getsize(path)
        else:
            self.__modify_time = None
            self.__size = None

    def is_exists(self):
        return exists(self.__path)

    def get_id(self):
        return self.__id

    def get_name(self):
        return self.__name

    def get_path(self):
        return self.__path

    def get_modify_time(self):
        return self.__modify_time

    def get_modify_time_repr(self):
        modify_time = self.__modify_time
        if modify_time is None:
            return None

        return strftime(self._TIME_FMT, gmtime(modify_time + self._TIME_OFFSET))

    def get_size(self):
        return self.__size

    def get_size_repr(self):
        size = self.__size
        if size is None:
            return None

        sizes = {}
        size_names = self._SIZES
        for size_name in size_names:
            sizes[size_name] = size % 1024
            size = size // 1024

        return next(
            f'{sizes[size_name]} {size_name}'
            for size_name in reversed(size_names)
            if sizes[size_name]
        )

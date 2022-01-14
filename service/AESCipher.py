import base64

from Crypto.Cipher import AES
from Crypto import Random


class AESCipher(object):
    _MODE = AES.MODE_CBC

    __slots__ = ('__key',)

    def __init__(self, key):
        super(AESCipher, self).__init__()

        self.__key = key

    def get_key(self):
        return self.__key

    def set_key(self, value):
        self.__key = value

    def encrypt(self, data):
        padded_data = self.__pad(data)
        iv = Random.new().read(AES.block_size)

        cipher = AES.new(self.__key, self._MODE, iv)

        encrypted_data = cipher.encrypt(padded_data)
        complex_data = iv + encrypted_data
        serialized_data = base64.b64encode(complex_data)

        return serialized_data

    def decrypt(self, serialized_data):
        complex_data = base64.b64decode(serialized_data)
        iv, encrypted_data = complex_data[:AES.block_size], complex_data[AES.block_size:]

        cipher = AES.new(self.__key, self._MODE, iv)

        padded_data = cipher.decrypt(encrypted_data)
        data = self.__unpad(padded_data)

        return data

    @staticmethod
    def __pad(data):
        block_size = AES.block_size
        data_size = len(data)
        pad_size = block_size - data_size % block_size

        return data.ljust(data_size + pad_size, bytes((pad_size,)))

    @staticmethod
    def __unpad(data):
        return data[:-data[-1]]

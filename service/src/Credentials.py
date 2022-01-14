import pickle
import hashlib

from src.AESCipher import AESCipher
from src.Common import check_master_key
from src.Constants import Constants
from os.path import exists


class Credentials(object):
    __slots__ = ('__data', '__cipher', '__messages', '__is_data_changed')

    def __init__(self, master_key_hash):
        super(Credentials, self).__init__()

        self.__data = None
        self.__is_data_changed = False
        self.__cipher = AESCipher(master_key_hash)
        self.__messages = []

    def __enter__(self):
        self.__data = self.__read_credentials_data()

        return self

    def __exit__(self, *args):
        self.__save_credentials_data()

        self.__data = None
        self.__is_data_changed = False
        self.__cipher = None
        self.__messages.clear()

    def add_node(self, service_name, node_name, node_value):
        if not (service_name and node_name):
            return

        data = self.__data
        service_credentials = data.setdefault(service_name, {})

        if node_value:
            service_credentials[node_name] = node_value
        else:
            service_credentials.pop(node_name, None)

        if not service_credentials:
            data.pop(service_name, None)

        self.__is_data_changed = True

    def set_master_key(self, new_master_key, new_master_key_repeat):
        if not (new_master_key and new_master_key_repeat):
            return

        if new_master_key != new_master_key_repeat:
            self.__add_message('Set master key: entered master keys are different!')
            return

        if not check_master_key(new_master_key):
            self.__add_message(
                f'Set master key: Master key has incorrect format!'
                ' It should have not less than {Constants.MasterKeyMinSize} lowercase, uppercase characters and digits'
            )
            return

        self.__cipher.set_key(self.get_key_hash(new_master_key))
        self.__is_data_changed = True
        self.__add_message('Master key was changed')

    def get_data(self):
        return self.__data

    def get_messages(self):
        return self.__messages

    def get_master_key_hash(self):
        return self.__cipher.get_key()

    @staticmethod
    def get_key_hash(key):
        key += Constants.Salt
        return hashlib.sha256(key.encode()).digest()

    def __read_credentials_data(self):
        if not exists(Constants.CredentialsPath):
            self.__add_message('Read credentials data: file was not found')
            return {}

        encrypted_data = open(Constants.CredentialsPath, 'rb').read()

        return self.__decrypt_credentials_data(encrypted_data)

    def __save_credentials_data(self):
        if not self.__is_data_changed:
            return

        encrypted_data = self.__encrypt_credentials_data()
        if encrypted_data is None:
            self.__add_message('Save credentials data: nothing to save')
            return

        with open(Constants.CredentialsPath, 'wb') as credentials_file:
            credentials_file.write(encrypted_data)

    def __encrypt_credentials_data(self):
        data = self.__data
        if data is None:
            self.__add_message('Encrypt credentials data: nothing to encrypt')
            return None

        serialized_data = pickle.dumps(data, protocol=pickle.HIGHEST_PROTOCOL)
        encrypted_data = self.__cipher.encrypt(serialized_data)

        return encrypted_data

    def __decrypt_credentials_data(self, encrypted_data):
        decrypted_data = self.__cipher.decrypt(encrypted_data)
        if not decrypted_data:
            self.__add_message('Decrypt credentials data: unable to decrypt data')
            return None

        try:
            deserialized_data = pickle.loads(decrypted_data)
        except pickle.UnpicklingError:
            self.__add_message('Decrypt credentials data: unable to unserialize data')
            return None

        return deserialized_data

    def __add_message(self, message):
        self.__messages.append(message)

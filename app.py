import pickle
import string

from AESCipher import AESCipher
from os.path import exists
from flask import Flask, escape, request, render_template


class Constants(object):
    AppName = 'Credentials Server'
    CredentialsPath = 'creds.bin'
    MasterKeyMinSize = 12


class Fields(object):
    # Common for all forms
    MasterKey = 'master_key'

    # Add service credentials node form
    ServiceName = 'service_name'
    NodeName = 'node_name'
    NodeValue = 'node_value'

    # Change Master Key form
    NewMasterKey = 'new_master_key'
    NewMasterKeyRepeat = 'new_master_key_repeat'

class Credentials(object):
    __slots__ = ('__data', '__cipher', '__messages')

    def __init__(self, master_key):
        super(Credentials, self).__init__()

        self.__data = None
        self.__cipher = AESCipher(master_key)
        self.__messages = []

    def __enter__(self):
        self.__data = self.__read_credentials_data()

        return self

    def __exit__(self, *args):
        self.__save_credentials_data()

        self.__data = None
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

    def set_master_key(self, new_master_key, new_master_key_repeat):
        if not (new_master_key and new_master_key_repeat):
            return

        if new_master_key != new_master_key_repeat:
            self.__add_message('Set master key: entered master keys are different!')
            return

        if not check_master_key(new_master_key):
            self.__add_message('Set master key: Master key has incorrect format! It should have not less than {:d} lowercase, uppercase characters and digits')
            return

        self.__cipher.set_key(new_master_key)

        self.__add_message('Master key was changed')

    def get_data(self):
        return self.__data

    def get_messages(self):
        return self.__messages

    def __read_credentials_data(self):
        if not exists(Constants.CredentialsPath):
            self.__add_message('Read credentials data: file was not found')
            return {}

        encrypted_data = open(Constants.CredentialsPath, 'rb').read()

        return self.__decrypt_credentials_data(encrypted_data)

    def __save_credentials_data(self):
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


def check_master_key(key):
    return (
        len(key) >= Constants.MasterKeyMinSize and
        any(c in string.ascii_lowercase for c in key) and
        any(c in string.ascii_uppercase for c in key) and
        any(c in string.digits for c in key)
    )


app = Flask(__name__)

@app.context_processor
def context_processor():
    return {
        'app_name': Constants.AppName
    }

@app.route("/", methods=['GET', 'POST'])
def main():
    if request.method == 'GET':
        master_key = new_master_key_data = new_node_data = None
    else:
        form_data = request.form

        master_key = form_data.get(Fields.MasterKey)
        new_master_key_data = tuple(map(form_data.get, (
            Fields.NewMasterKey,
            Fields.NewMasterKeyRepeat
        )))
        new_node_data = tuple(map(form_data.get, (
            Fields.ServiceName,
            Fields.NodeName,
            Fields.NodeValue
        )))

    if not master_key:
        return render_template('start.html')

    if not check_master_key(master_key):
        return render_template('start.html', error='Invalid master key format')

    with Credentials(master_key) as credentials:
        credentials_data = credentials.get_data()
        if credentials_data is None:
            return render_template(
                'start.html',
                error='Unable to get credentials data',
                messages=credentials.get_messages()
            )

        if new_master_key_data is not None:
            credentials.set_master_key(*new_master_key_data)

        if new_node_data is not None:
            credentials.add_node(*new_node_data)

        return render_template(
            'session.html',
            master_key=escape(master_key),
            credentials=credentials_data,
            messages=credentials.get_messages()
        )

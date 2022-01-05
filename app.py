import pickle

from AESCipher import AESCipher
from os.path import exists
from flask import Flask, escape, request, render_template

class Constants(object):
    AppName = 'Credentials Server'
    CredentialsPath = 'creds.bin'


class Fields(object):
    # Common for all forms
    MasterKey = 'master_key'

    # Add service credentials node form
    ServiceName = 'service_name'
    NodeName = 'node_name'
    NodeValue = 'node_value'


class Credentials(object):
    __slots__ = ('__data', '__cipher')

    def __init__(self, master_key):
        super(Credentials, self).__init__()

        self.__data = None
        self.__cipher = AESCipher(master_key)

    def __enter__(self):
        self.__data = self.__read_credentials_data()

        return self

    def __exit__(self, *args):
        print(f'args: {args}')
        self.__save_credentials_data()

        self.__data = None
        self.__cipher = None

    def add_node(self, new_node_data):
        if not all(new_node_data):
            return

        service_name, node_name, node_value = new_node_data

        service_credentials = self.__data.setdefault(service_name, {})
        service_credentials[node_name] = node_value

    def get_data(self):
        return self.__data

    def __read_credentials_data(self):
        if not exists(Constants.CredentialsPath):
            return {}

        encrypted_data = open(Constants.CredentialsPath, 'rb').read()

        return self.__decrypt_credentials_data(encrypted_data)

    def __save_credentials_data(self):
        with open(Constants.CredentialsPath, 'wb') as credentials_file:
            credentials_file.write(self.__encrypt_credentials_data())

    def __encrypt_credentials_data(self):
        serialized_data = pickle.dumps(self.__data, protocol=pickle.HIGHEST_PROTOCOL)
        encrypted_data = self.__cipher.encrypt(serialized_data)

        return encrypted_data

    def __decrypt_credentials_data(self, encrypted_data):
        decrypted_data = self.__cipher.decrypt(encrypted_data)
        if not decrypted_data:
            return None

        deserialized_data = pickle.loads(decrypted_data)

        return deserialized_data


_SOME_CREDS = {
    'inst': {
        'login': 'some',
        'pass': 'some'
    }
}

app = Flask(__name__)

@app.context_processor
def context_processor():
    return {
        'app_name': Constants.AppName
    }

@app.route("/", methods=['GET', 'POST'])
def main():
    if request.method == 'GET':
        master_key = new_node_data = None
    else:
        form_data = request.form

        master_key = form_data.get(Fields.MasterKey)
        new_node_data = tuple(map(form_data.get, (
            Fields.ServiceName,
            Fields.NodeName,
            Fields.NodeValue
        )))

    if not master_key:
        return render_template('start.html')

    with Credentials(master_key) as credentials:
        credentials_data = credentials.get_data()
        if credentials_data is None:
            return render_template('start.html', error='Invalid master key')

        if new_node_data is not None:
            credentials.add_node(new_node_data)

        return render_template(
            'session.html',
            master_key=escape(master_key),
            credentials=credentials_data
        )

import codecs

from src.Common import check_master_key
from src.Constants import Constants, Fields
from src.Credentials import Credentials
from flask import Flask, escape, request, render_template


app = Flask(__name__, root_path=Constants.AppRoot)


@app.context_processor
def context_processor():
    return {
        'app_name': Constants.AppName
    }


@app.route("/", methods=['GET', 'POST'])
def main():
    if request.method == 'GET':
        master_key = master_key_hash = new_master_key_data = new_node_data = None
    else:
        form_data = request.form

        master_key = form_data.get(Fields.MasterKey)
        master_key_hash = form_data.get(Fields.MasterKeyHash)
        new_master_key_data = tuple(map(form_data.get, (
            Fields.NewMasterKey,
            Fields.NewMasterKeyRepeat
        )))
        new_node_data = tuple(map(form_data.get, (
            Fields.ServiceName,
            Fields.NodeName,
            Fields.NodeValue
        )))

    if master_key:
        if not check_master_key(master_key):
            return render_template('start.html', error='Invalid master key format')

        master_key_hash = Credentials.get_key_hash(master_key)
    elif master_key_hash:
        master_key_hash = codecs.decode(master_key_hash, 'hex')
    else:
        return render_template('start.html')

    with Credentials(master_key_hash) as credentials:
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
            master_key_hash=escape(codecs.encode(credentials.get_master_key_hash(), 'hex').decode()),
            credentials=credentials_data,
            messages=credentials.get_messages()
        )

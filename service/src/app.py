from src.Constants import Constants, Fields
from src.Credentials import Credentials
from src.CredentialsManager import CredentialsManager
from flask import Flask, abort, request, render_template, send_file


app = Flask(__name__, root_path=Constants.AppRoot)


@app.route('/favicon.ico')
def favicon():
    return app.send_static_file('favicon.ico')


@app.context_processor
def context_processor():
    return {
        'app_name': Constants.AppName
    }


@app.route(f'/{Constants.CredentialsPrefix}<id_>{Constants.CredentialsExt}')
def credentials_getter(id_):
    if not id_.isdigit():
        abort(403)

    credentials = Credentials(int(id_))
    if not credentials.is_exists():
        abort(404)

    return send_file(credentials.get_path())


@app.route("/", methods=['GET', 'POST'])
def main():
    credentials_manager = CredentialsManager()

    if request.method == 'GET':
        credentials_file = None
    else:
        credentials_file = request.files.get(Fields.CredentialsFile)

    if credentials_file is not None:
        credentials_manager.upload_credentials(credentials_file)

    return render_template(
        'start.html',
        credentials_list=credentials_manager.get_credentials_list(),
        messages=credentials_manager.get_messages(),
        error=credentials_manager.get_error()
    )

import re

from os import listdir

from src.Constants import Constants
from src.Credentials import Credentials


class CredentialsManager(object):
    __slots__ = ('__credentials_list', '__messages', '__error')

    def __init__(self):
        super(CredentialsManager, self).__init__()

        self.__credentials_list = list(self.__iter_credentials())
        self.__messages = []
        self.__error = None

    def get_credentials_list(self):
        return self.__credentials_list

    def get_messages(self):
        return self.__messages

    def get_error(self):
        return self.__error

    def upload_credentials(self, credentials_file):
        if not credentials_file or not credentials_file.filename:
            self.__error = 'No file was selected'
            return

        if not self.__is_valid_file(credentials_file):
            self.__error = 'File is not valid!'
            return

        credentials_list = self.__credentials_list
        if credentials_list:
            credentials_id = max(credentials.get_id() for credentials in credentials_list) + 1
        else:
            credentials_id = 1

        credentials = Credentials(credentials_id)
        credentials_file.save(credentials.get_path())
        credentials.update()
        credentials_list.append(credentials)

        self.__messages.append(f'Credentials file with id {credentials_id} was uploaded!')

    @staticmethod
    def __iter_credentials():
        credentials_matcher = re.compile(Constants.CredentialsNamePattern)

        for credentials_name in listdir(Constants.CredentialsDir):
            credentials_match = credentials_matcher.match(credentials_name)
            if credentials_match is None:
                continue

            credentials_id, = credentials_match.groups()
            credentials_id = int(credentials_id)

            yield Credentials(credentials_id)

    @staticmethod
    def __is_valid_file(credentials_file):
        return credentials_file.filename.endswith(Constants.CredentialsExt)
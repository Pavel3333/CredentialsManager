import os


class Constants(object):
    AppName = 'Credentials Manager'
    AppRoot = os.getenv('APP_FOLDER')
    CredentialsDir = os.path.join(AppRoot, 'data')
    CredentialsPrefix = 'credentials_'
    CredentialsExt = '.enpassbackup'
    CredentialsNameFmt = f'{CredentialsPrefix}{{:d}}{CredentialsExt}'
    CredentialsNamePattern = f'{CredentialsPrefix}(\\d+)\\{CredentialsExt}'
    MasterKeyMinSize = 12

    SaltSize = 10
    Salt = '\xa0\x05\xb9n\x84\xcdg\x07\x19T'  # os.urandom(SaltSize)


class Fields(object):
    # Upload form
    CredentialsFile = 'credentials_file'

    # Session key hash
    MasterKeyHash = 'master_key_hash'

    # Add service credentials node form
    ServiceName = 'service_name'
    NodeName = 'node_name'
    NodeValue = 'node_value'

    # Change Master Key form
    NewMasterKey = 'new_master_key'
    NewMasterKeyRepeat = 'new_master_key_repeat'

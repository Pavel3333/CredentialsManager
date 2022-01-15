import os


class Constants(object):
    AppName = 'Credentials Server'
    AppRoot = os.getcwd()
    CredentialsPath = os.path.join(AppRoot, 'data', 'creds.bin')
    MasterKeyMinSize = 12

    SaltSize = 10
    Salt = '\xa0\x05\xb9n\x84\xcdg\x07\x19T'  # os.urandom(SaltSize)


class Fields(object):
    # Common for all forms
    MasterKey = 'master_key'

    # Session key hash
    MasterKeyHash = 'master_key_hash'

    # Add service credentials node form
    ServiceName = 'service_name'
    NodeName = 'node_name'
    NodeValue = 'node_value'

    # Change Master Key form
    NewMasterKey = 'new_master_key'
    NewMasterKeyRepeat = 'new_master_key_repeat'

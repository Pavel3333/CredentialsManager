import string

from Constants import Constants


def check_master_key(key):
    return (
        len(key) >= Constants.MasterKeyMinSize and
        any(c in string.ascii_lowercase for c in key) and
        any(c in string.ascii_uppercase for c in key) and
        any(c in string.digits for c in key)
    )

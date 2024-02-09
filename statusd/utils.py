from string import ascii_letters, digits


def error_resp(message):
    return {
        'status': 'error',
        'message': message
    }


def success_resp(message):
    return {
        'status': 'success',
        'message': message
    }


def simple_sanitize(string):
    valid_charset = set(ascii_letters + digits + '_' + '-')
    string = string.replace(' ', '-')
    return ''.join(x for x in string if x in valid_charset)

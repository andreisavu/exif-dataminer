
from urllib import quote

def can_quote(s):
    try:
        quote(s)
    except KeyError:
        return False
    return True


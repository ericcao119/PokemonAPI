

def separate_conjuctive(a: str):
    r""" DO NOT USE THIS FUNCTION IF YOU ARE UNSURE OF THE FORM OF THE INPUT.
    This is a very specific function for capturing strings of the form:
    'a and b and c ...' or
    'a, b, c, ..., and d'

    It returns a list of the form [a, b, c, d, ...]
    """
    # TODO: Make this more generalizable

    if ',' in a:
        return [i.replace(' and ', '').strip() for i in a.split(',')]
    elif ' and ' in a:
        return [i.strip() for i in a.split(' and ')]
    else:
        return [a]

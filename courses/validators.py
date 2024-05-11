import re


def validate_semester(value):
    value = value.lower()
    return re.match(r'i[v|i]?\/i{1,2}$', value)

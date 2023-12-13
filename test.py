from ast import literal_eval

def list_to_string(my_list):
    """
    Convert a list of tuples to a string representation.
    """
    return ', '.join('({}, {}, {})'.format(*item) for item in my_list)

def string_to_list(result_string):
    """
    Convert a string representation back to a list of tuples.
    """
    return literal_eval(f'[{result_string}]')

data = [(12.52,456.52,43.123),(12.52,456.52,43.123),(12.52,456.52,43.123),(12.52,456.52,43.123),(12.52,456.52,43.123)]

string_test = list_to_string(data)
print(list_to_string(data))
print(type(string_to_list(string_test)))
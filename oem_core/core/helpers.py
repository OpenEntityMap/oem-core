def convert_keys_to_string(value):
    if type(value) is not dict:
        return value

    result = {}

    for k, v in value.items():
        if type(k) is not str:
            k = str(k)

        if v is None:
            continue

        if type(v) is dict:
            result[k] = convert_keys_to_string(v)
        elif type(v) is list:
            result[k] = [
                convert_keys_to_string(v)
                for v in v
            ]
        else:
            result[k] = v

    return result


def get_attribute(touched, data, key, default=None):
    try:
        value = data[key]

        touched.add(key)
        return value
    except KeyError:
        return default

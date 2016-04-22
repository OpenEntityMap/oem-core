import inspect


class Protocol(object):
    __built = False
    __encode_map = {}
    __protocols = {}

    __key__ = None

    __ignore__ = False
    __root__ = False

    @classmethod
    def build(cls):
        if cls.__built:
            return

        cls.__decode_map = {}
        cls.__encode_map = {}

        cls.__protocols = {}

        for key, value in cls.__dict__.items():
            if key.startswith('__') or key.startswith('_Protocol__'):
                continue

            if type(value) is int:
                cls.__decode_map[value] = key
                cls.__encode_map[key] = value
            elif inspect.isclass(value):
                cls.__protocols[value.__key__] = value
            else:
                raise ValueError('Unknown property in protocol (key: %r)' % key)

        cls.__built = True

    @classmethod
    def get_protocol(cls, name):
        if name not in cls.__protocols:
            raise ValueError('Missing definition in %r for protocol %r' % (cls, name))

        return cls.__protocols[name]

    @classmethod
    def decode_key(cls, key):
        if key not in cls.__decode_map:
            raise ValueError('Missing definition in %r for key %r' % (cls, key))

        return cls.__decode_map[key]

    @classmethod
    def encode_key(cls, key):
        if key not in cls.__encode_map:
            raise ValueError('Missing definition in %r for key %r' % (cls, key))

        return cls.__encode_map[key]

    @classmethod
    def get_value(cls, data, key, default=None):
        try:
            return data[str(key)]
        except KeyError:
            try:
                return data[key]
            except KeyError:
                return default


class Minimize(object):
    @classmethod
    def decode(cls, data, protocol):
        if protocol.__ignore__:
            return data

        # Ensure protocol is built
        protocol.build()

        # Process each item in `data`
        result = {}

        for key, value in data.items():
            # Ignore "minimized" item identifier
            if key == '~':
                continue

            # Decode `key` with `protocol`
            key = protocol.decode_key(key)

            # Process child protocols
            if type(value) is dict:
                # Decode `value` with `protocol`
                value = cls.decode(value, protocol.get_protocol(key))
            elif type(value) is list:
                # Decode items in `value` with `protocol`
                value = [
                    (
                        cls.decode(value, protocol.get_protocol(key))
                        if type(value) is dict else value
                    )
                    for value in value
                ]

            # Store item
            result[key] = value

        return result

    @classmethod
    def encode(cls, data, protocol):
        if protocol.__ignore__:
            return data

        # Ensure protocol is built
        protocol.build()

        # Process each item in `data`
        result = {}

        for key, value in data.items():
            # Process child protocols
            if type(value) is dict:
                # Encode `value` with `protocol`
                value = cls.encode(value, protocol.get_protocol(key))
            elif type(value) is list:
                # Encode items in `value` with `protocol`
                value = [
                    (
                        cls.encode(value, protocol.get_protocol(key))
                        if type(value) is dict else value
                    )
                    for value in value
                ]

            # Encode `key` with `protocol`
            key = protocol.encode_key(key)

            # Store item
            result[key] = value

        if protocol.__root__:
            # Set "minimal" flag
            result['~'] = '~'

        return result

class DataBag(object):
    _data = {}

    @classmethod
    def get(cls, key):
        def get_from(items, data):
            """Recursively get value from dictionary deep key.

            Args:
                items (list): List of dictionary keys
                data (dict): Portion of dictionary to operate on

            Returns
                object: Value from dictionary

            Raises:
                KeyError: If key does not exist
            """
            it = items.pop(0)
            data = data[it]
            if items:
                return get_from(items, data)
            else:
                return data

        return get_from(key.split('.'), cls._data)

    @classmethod
    def add(cls, key, value):
        def set_to(items, data):
            """Recursively set value to dictionary deep key.

            Args:
                items (list): List of dictionary keys
                data (dict): Portion of dictionary to operate on
            """
            item = items.pop(0)

            # Traverse dictionary to last item key
            if items:
                if item not in data:
                    data[item] = {}
                set_to(items, data[item])
            # Set Value on last key
            else:
                # If the key already exists and is not a list -> transfrom to list and append value
                if item in data:
                    if not isinstance(data[item], list):
                        data[item] = [data[item]]
                    data[item].append(value)
                else:
                    data[item] = value

        set_to(key.split('.'), cls._data)

    @classmethod
    def merge(cls, key, data):
        if key in cls._data:
            if isinstance(cls._data[key], dict):
                cls._data[key].update(data)
            elif isinstance(cls._data[key], list):
                cls._data[key].extend(data)

    @classmethod
    def all(cls):
        return cls._data

    @classmethod
    def clear(cls):
        cls._data = {}

    @classmethod
    def flush(cls, key=None):
        if key and key in cls._data:
            data = cls.get(key)
            cls.delete(key)
            return data

        data = cls.all()
        cls.clear()
        return data

    @classmethod
    def delete(cls, key):
        def del_key(items, data):
            """Recursively remove deep key from dict.

            Args:
                items (list): List of dictionary keys
                data (dict): Portion of dictionary to operate on

            Raises:
                KeyError: If key does not exist
            """
            item = items.pop(0)
            if items and item in data:
                return del_key(items, data[item])
            elif not items and item in data:
                del data[item]
            elif not items and item not in data:
                raise KeyError(item)

        del_key(key.split('.'), cls._data)

class DataBag(object):
    _data = {}

    @classmethod
    def add(cls, key, data):
        if key in cls._data:
            if not isinstance(cls._data[key], list):
                cls._data[key] = [cls._data[key]]
            cls._data[key].append(data)
        else:
            cls._data[key] = data

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
    def flush(cls):
        data = cls.all()
        cls.clear()
        return data

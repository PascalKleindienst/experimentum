"""In-Memory Container to easily store experiment results on the fly.

Adding Entries
--------------
Add the entry `{'foo': {'bar': {'baz': 42} }}` to the DatBag via a dot-notation supported key::

    DataBag.add('foo.bar.baz', 42)

Mergins Entries
---------------
Merging dictionary and list entires::

    DataBag.add('foo.bar', [1, 2, 3])
    DataBag.add('foo.baz', {'a': 1, 'b': 2})
    DataBag.merge('foo.bar', [2, 4, 8])
    DataBag.merge('foo.baz', {'a': 42, 'c': 3})

    # Results in
    # {
    #   'foo': {
    #       'bar': [1, 2, 3, 2, 4, 8],
    #       'baz': {'a': 42, 'b': 2, 'c': 3}
    #   }
    # }


Getting Entries
---------------
Add the entry `baz` of the dictionary `{'foo': {'bar': {'baz': 42} }}` in the DatBag via a
dot-notation supported key::

    data = DataBag.get('foo.bar.baz')  # 42

The DataBag also provides a default value if the key does not exist
    data = DataBag.get('a.b.c', 'default value')  # 'default value'


Deleting Entries
----------------
Deleting entries works just like adding/getting entries::

    DataBag.delete('foo.bar.baz')  # {'foo': {'bar': {}}}


Flushing Entries
----------------
Flushing the DataBag means that you get all the entires (or just a specific key)
and then clear the content::

    DataBag.add('foo.bar.baz', 42)
    print(DataBag.flush('foo.bar.baz))  # prints: 42, contains: {'foo': {'bar': {}}}
    print(DataBag.flush())              # prints: {'foo': {'bar': {}}}, contains: {}}

"""


def set_to(items, data, value):
    """Recursively set value to dictionary deep key.

    Args:
        items (list): List of dictionary keys
        data (dict): Portion of dictionary to operate on
        value (object): Value to set for key.
    """
    item = items.pop(0)

    # Traverse dictionary to last item key
    if items:
        if item not in data:
            data[item] = {}
        set_to(items, data[item], value)
    # Set Value on last key
    else:
        # If the key already exists and is not a list -> transfrom to list and append value
        if item in data:
            if not isinstance(data[item], list):
                data[item] = [data[item]]
            data[item].append(value)
        else:
            data[item] = value


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
    if not isinstance(data, dict):
        raise KeyError

    item = items.pop(0)
    data = data[item]

    return get_from(items, data) if items else data


def del_key(items, data):
    """Recursively remove deep key from dict.

    Args:
        items (list): List of dictionary keys
        data (dict): Portion of dictionary to operate on

    Raises:
        KeyError: If key does not exist
    """
    if not isinstance(data, dict):
        raise KeyError

    item = items.pop(0)
    if items and item in data:
        return del_key(items, data[item])
    elif not items and item in data:
        del data[item]
    elif not items and item not in data:
        raise KeyError(item)


class DataBag(object):

    """In-Memory Container to easily store experiment results on the fly."""
    _data = {}

    @classmethod
    def add(cls, key, value):
        """Add an item to the DatBag via a dot-notation supported key.

        Args:
            key (str): Key to set (i.e. 'foo' or 'foo.bar.baz' for a deep key)
            value (object): Value to set for key.
        """
        set_to(key.split('.'), cls._data, value)

    @classmethod
    def get(cls, key, default=None):
        """Get an item from the DataBag via a dot-notation supported key.

        Args:
            key(str): Key to get (i.e. 'foo' or 'foo.bar.baz' for a deep key)
            default(object, optional): Defaults to None. Default if key does not exist

        Returns:
            object: Value of the key
        """
        try:
            return get_from(key.split('.'), cls._data)
        except KeyError:
            return default

    @classmethod
    def delete(cls, key):
        """Delete an item from the DataBag via a dot-notation supported key.

        Args:
            key(str): Key to delete (i.e. 'foo' or 'foo.bar.baz' for a deep key)

        Returns:
            int: Statuscode, 1: okay, -1: Key not found
        """
        try:
            del_key(key.split('.'), cls._data)
        except KeyError:
            return -1

        return 1

    @classmethod
    def merge(cls, key, data):
        """Merge two dicts or lists.

        For example:
            - {'a': 1, 'b': 2} + {'a': 42, 'c': 3}  => {'a': 42, 'b': 2, 'c': 3}
            - ['a', 'b', 'c']  + ['a', 'd', 'e']    => ['a', 'b', 'c', 'a', 'd', 'e']

        Args:
            key (str): Key to set (i.e. 'foo' or 'foo.bar.baz' for a deep key)
            data (dict|list): Value to update/extend for key.
        """
        items = cls.get(key)

        if items:
            if isinstance(items, dict):
                items.update(data)
            elif isinstance(items, list):
                items.extend(data)

    @classmethod
    def all(cls):
        """Return content of the DataBag.

        Returns:
            dict: DataBag content.
        """
        return cls._data

    @classmethod
    def clear(cls):
        """Clear DataBag content."""
        cls._data = {}

    @classmethod
    def flush(cls, key=None, default=None):
        """Flush a specific key or all of the databag (i.e. return and delete).

        Args:
            key(str): Key to set(i.e. 'foo' or 'foo.bar.baz' for a deep key)
            default(object, optional): Defaults to None. Default if key does not exist

        Returns:
            object: Value of the key
        """
        # flush specific key
        if key:
            data = cls.get(key, default)
            cls.delete(key)
            return data

        # flush all
        data = cls.all()
        cls.clear()
        return data

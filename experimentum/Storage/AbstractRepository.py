"""Interface for using the *Repository Design Pattern*.

Instead of using the :py:class:`.AbstractStore` (or any of its implementations like
:py:class:`.Store`) as a *God Class* the *Repository Design Pattern*
allows you to follow the *Single Responsibility Rule*.

A Repository acts like an in-memory domain object collection, that connects the domain
and data mapping layers. Objects can be easily added to and removed from the Repository,
due to the mapping code of the Repository which will ensure that the right operations
are executed behind the scenes.

Apart from acting as a bridge between the data and the domain layer, the Repository
also provides some useful methods for storing, updating, deleting and querying data.

Examples
========
Lets assume that you are using the default experimentum data store :py:mod:`.Store`.
With :py:mod:`.Repository` there is already an implementation which will handle
the mapping between the Repository objects and the SQLAlchemy ORM which is used by
the :py:mod:`.Store`.

For simplicity we will assume that your database already contains a *User* and
*Address* table (for more information on how to specify your domain layer, see:
:py:mod:`.Migrations`).

Data Layer
----------
Each user has a ``name``, ``fullname`` and a ``password``
field and can have multiple ``adresses``. Each address has an ``email`` field::

    from experimentum.Storage import AbstractRepository


    class AddressRepository(AbstractRepository.implementation):
        __table__ = 'Address'

        def __init__(self, email):
            self.email = email


    class UserRepository(AbstractRepository.implementation):
        __table__ = 'User'

        __relationships__ = {
            'addresses': [AddressRepository]
        }

        def __init__(self, name, fullname, password):
            self.name = name
            self.fullname = fullname
            self.password = password

In the ``__init__`` method of the repository you specify the fields of the table.
The ``__table__`` attribute contains the name of the table, while the optional
``__relationships__`` attribute specifies any relationships of the data.
The key is the attribute under which the data will be accessible, ie::

    print(user.addresses)  # will print all addresses of a specific user

Actions
-------
There are several methods for querying data, like :py:meth:`~.Repository.find`,
:py:meth:`~.Repository.get`, :py:meth:`~.Repository.first`, :py:meth:`~.Repository.all`::

    # Find a user by its id
    user = UserRepository.find(2)  # get user with ID 2
    print(user.id, user.name, user.fullname, user.addresses)

    # Get many users by a condition (here where name != 'John')
    users = UserRepository.get(where=['name', '!=', 'John'])
    for user in users:
        print(user.id, user.name, user.fullname, user.addresses)

    # Get the first user which satisfies a certain condition
    user = UserRepository.first(where=['name', 'John'])
    print(user.id, user.name, user.fullname, user.addresses)

    # Get all users
    users = UserRepository.all()
    for user in users:
        print(user.id, user.name, user.fullname, user.addresses)

The :py:class:`.Repository` class also provides several methods for storing, updating, and
deleting data, like :py:meth:`~.Repository.create`, :py:meth:`~.Repository.update`
:py:meth:`~.Repository.delete`::

    # Create a new user from a data dictionary
    user = UserRepository.from_dict({
        'name': 'Hello',
        'fullname': 'World',
        'password': '1234',
        # Turns the entries into AddressRepository instances and adds them to the user repo
        # so that they get saved with the correct user id
        'addresses': [
            {'email': 'hello@world.com'},
            {'email': 'foo@world.com'},
        ]
    })
    user.create()  # create the new user

    # Update a user
    user = UserRepository.find(2)
    user.fullname = 'Doe'
    user.name = 'John'
    user.update()

    # Delete a user
    user = UserRepository.find(1)
    user.delete()

Events
------
A Repository provides several events, allowing you to hook into the following points in a
repositorie's lifecycle: :py:meth:`~.AbstractRepository.before_insert`,
:py:meth:`~.AbstractRepository.after_insert`, :py:meth:`~.AbstractRepository.before_update`,
:py:meth:`~.AbstractRepository.after_update`.

Events allow you to easily execute code each time after/before a specific repository object
is saved or updated in the data store.

::

    class AddressRepository(AbstractRepository.implementation):
        # ...

        def after_insert(self):
            print('Gets called each time after an address is saved to the database.')
            print(self.id, self.email)  # Object has access to the inserted id

Loading
-------
In order for the framework to map all the repositories it has to load them via the
:py:class:`~.RepositoryLoader` class. For the :py:class:`~.RepositoryLoader` class
to be able to find the repositories, the files have be in your repository folder and
end with ``Repository.py``. The repository files should contain a repository class with
the same name as the file name.
"""
import os
import sys
import json
from six import add_metaclass
from abc import abstractmethod, ABCMeta
from experimentum.cli import print_failure
from experimentum.utils import find_files


class RepositoryLoader(object):

    """Load and map all the repositories it can find and cache them.

    Attributes:
        app (App): Main App class.
        implementation (AbstractRepository): Concrete repo implementation which should be used.
        store (AbstractStore): Data store which is used
    """

    def __init__(self, app, implementation, store):
        """Set up loader.

        Args:
            app (App): Main App class.
            implementation (AbstractRepository): Concrete repo implementation which should be used.
            store (AbstractStore): Data store which is used
        """
        self.app = app
        self.implementation = implementation
        self.store = store
        self._repos = {}

        AbstractRepository.implementation = implementation

    def _import_file(self, name, loc):
        """Load the repository file modules.

        Args:
            name (str): Name of the Repository
            loc (str): Location of the Repository

        Returns:
            Module: Repository Module

        Raises:
            Error: if the module could not be found
        """
        path = self.app.config.get('storage.repositories.path', 'repositories')

        if sys.version_info >= (3, 5):
            import importlib.util
            import importlib.machinery

            # finder is needed when folder is not a subfolder of root dir (e.g. for test layouts)
            loader_details = (
                importlib.machinery.SourceFileLoader,
                importlib.machinery.SOURCE_SUFFIXES
            )

            finder = importlib.machinery.FileFinder(loc, loader_details)
            spec = finder.find_spec(name)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            return module

        else:
            import imp
            # first find and load the package assuming it is in
            # the current working directory, '.'
            fp, p, desc = imp.find_module(os.path.join(self.app.root, path), ['.'])
            pkg = imp.load_module(path, fp, p, desc)

            # then find the named repository module using pkg.__path__
            # and load the module using the dotted name
            fp, p, desc = imp.find_module(name, pkg.__path__)
            module = imp.load_module(path + '.' + name, fp, p, desc)
            fp.close()

            return module

    def load(self):
        """Load all repositories from the repo folder and try to map them to the store."""
        # Get Repository files
        files = find_files(
            self.app.root,
            self.app.config.get('storage.repositories.path', 'repositories')
        )

        for filename in files:
            name = os.path.basename(filename)[:-3]

            # Try to load and map the repos
            try:
                module = self._import_file(name, os.path.abspath(os.path.dirname(filename)))
                repo = getattr(module, name)
                repo.mapping(repo, self.store)
                self._repos[name] = repo

            except Exception as exc:
                print_failure('Could not load repository. ' + str(exc), exit_code=1)

    def get(self, repository):
        """Return class of a loaded repository if it exists.

        Args:
            repository (str): Name of repository class.

        Returns:
            AbstractRepository: Repository class
        """
        repo = self._repos.get(repository, None)

        if repo is None:
            print_failure(
                'Could not load repository {}. Are you sure it exists?'.format(repository),
                exit_code=1
            )

        return repo


@add_metaclass(ABCMeta)
class AbstractRepository(object):

    """Interface for using the *Repository Design Pattern*.

    Instead of using the :py:class:`.AbstractStore` as a *God Class* the
    *Repository Design Pattern*  allows you to follow the *Single Responsibility Rule*.

    Attributes:
        store (AbstractStore): Store that is used for mapping domain and data layer.
        implementation(AbstractRepository): Concrete repo implementation which should be used.
        __table__ (str): Name of the table the repository refers to.
        __relationship__ (dict): Any Relationships the data has.
    """

    implemantation = None
    store = None
    __table__ = ''
    __relationships__ = {}

    def __init__(self, **attributes):
        """Set all attributes which where passed as kwargs."""
        for attr, val in attributes.items():
            self[attr] = val

    def to_json(self):
        """Return JSON representation of repository fields and values.

        Returns:
            str: JSON representration
        """
        attrs = {k: v for k, v in self.__dict__.items() if k[:1] != '_'}
        return json.dumps(attrs, sort_keys=True, indent=4)

    def __repr__(self):
        """Human readable representation of repository fields and values.

        Returns:
            str: human readable representation
        """
        attrs = ['{}="{}"'.format(k, v) for k, v in self.__dict__.items() if k[:1] != '_']
        return '<{} {} />'.format(self.__class__.__name__, ' '.join(attrs))

    def __contains__(self, key):
        """Check if repository has a certain attribute.

        Args:
            key (str): Attribute to check

        Returns:
            bool: Whether the attribute exists or not
        """
        return hasattr(self, key)

    def __getitem__(self, key):
        """Get attribute value with dictionary like syntax.

        Args:
            key (str): Attribute Key

        Returns:
            object: Attribute value
        """
        return getattr(self, key)

    def __setitem__(self, key, item):
        """Set attribute value with dictionary like syntax.

        Args:
            key (str): Attribute Key
            item (object): Attribute value
        """
        setattr(self, key, item)

    @classmethod
    def from_dict(cls, data):
        """Create a new Repository instance based on a dictionary entry.

        Args:
            data (dict): Repository Data

        Returns:
            AbstractRepository: Repository instance filled with data.
        """
        init = {}
        relations = {}
        relationships = cls.__relationships__

        for key, val in data.items():
            if key in relationships:
                if type(val) is list:
                    relations[key] = [relationships[key][0].from_dict(v) for v in val]
                else:
                    relations[key] = [relationships[key][0].from_dict(val)]
            else:
                init[key] = val

        repo = cls(**init)

        for key, val in relations.items():
            repo[key] = val

        return repo

    @staticmethod
    def mapping(cls, store):
        """Map data store content to repository classes.

        Example:
        Map a *User* Table in the data store to the *UserRepository*,
        which reflects the attributes of the User Table schema.

        Args:
            cls (AbstractRepository): Repository to map
            store (AbstractStore): Storage that is used

        Raises:
            NotImplementedError: if method is not implemented
        """
        raise NotImplementedError('Must implement mapping method!')

    @abstractmethod
    def create(self):
        """Save the repository content in your data store.

        Raises:
            NotImplementedError: if method is not implemented yet.
        """
        raise NotImplementedError('Must implement create method!')

    @abstractmethod
    def update(self):
        """Update the repository content in your data store.

        Raises:
            NotImplementedError: if method is not implemented yet.
        """
        raise NotImplementedError('Must implement update method!')

    @abstractmethod
    def delete(self):
        """Delete the repository content from your data store.

        Raises:
            NotImplementedError: if method is not implemented yet.
        """
        raise NotImplementedError('Must implement delete method!')

    @classmethod
    def get(cls, where=None):
        """Get all entries which satisfy a specific condition from your data store.

        Args:
            where (list, optional): Defaults to None. Where Condition

        Raises:
            NotImplementedError: if method is not implemented yet.

        Returns:
            list: List of items which satisfy the condition.
        """
        raise NotImplementedError('Must implement get method!')

    @classmethod
    def first(cls, where=None):
        """Get first entry which satisfy a specific condition from your data store.

        Args:
            where (list, optional): Defaults to None. Where Condition

        Raises:
            NotImplementedError: if method is not implemented yet.

        Returns:
            AbstractRepository: Item which satisfies the condition.
        """
        raise NotImplementedError('Must implement first method!')

    @classmethod
    def all(cls):
        """Get all entries for this specific repository from your data store.

        Raises:
            NotImplementedError: if method is not implemented yet.

        Returns:
            list: List of all entires
        """
        raise NotImplementedError('Must implement all method!')

    @classmethod
    def find(cls, id):
        """Find an entry of this repository based on its id.

        Args:
            id (int): ID to search for.

        Raises:
            NotImplementedError: if method is not implemented yet.

        Returns:
            AbstractRepository: Item which the concrete id
        """
        raise NotImplementedError('Must implement find method!')

    def before_insert(self):
        """Event that gets called before insert statement is executed.

        Returns:
            None
        """
        return None

    def after_insert(self):
        """Event that gets called after insert statement is executed.

        Returns:
            None
        """
        return None

    def before_update(self):
        """Event that gets called before update statement is executed.

        Returns:
            None
        """
        return None

    def after_update(self):
        """Event that gets called after update statement is executed.

        Returns:
            None
        """
        return None

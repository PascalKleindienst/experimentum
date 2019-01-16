"""Implementation of the AbstractRepository.

Implements the AbstractRepository interface to use the
SQLAlchemy ORM as a data store.
"""
from sqlalchemy.orm import mapper, relationship
from sqlalchemy.event import listen
from sqlalchemy import or_
from experimentum.Storage import AbstractRepository
import logging


class QueryBuilder(object):

    """Helper Class to build a SQLAlchemy Query.

    Attributes:
        repo (Repository): The Repository to query
        where (list): where condition to build
        __filter_cond (list): Filter Conditions
        __filter_cond_or (list): Filter Conditions that are connected with logical OR
    """

    def __init__(self, repo, where):
        """Set up query builder.

        Args:
            repo (Repository): Repository to query.
            where (list): where condition to build.
        """
        self.__filter_cond = []
        self.__filter_cond_or = []

        self.repo = repo

        if not isinstance(where, list):
            where = []
        if len(where) is 0 or not isinstance(where[0], list):
            where = [where]

        self.where = where

    def build(self, query):
        """Build the query.

        Args:
            query (sqlalchemy.orm.query.Query): Current query

        Returns:
            sqlalchemy.orm.query.Query: Final query
        """
        query = self.build_where(query)
        return query

    def build_where(self, query):
        """Build the query with the where conditions.

        Args:
            query (sqlalchemy.orm.query.Query): Current Query

        Returns:
            sqlalchemy.orm.query.Query: Query with where conditions applied.
        """
        for cond in self.where:
            # ['id', 2] => WHERE id == 2
            if len(cond) is 2:
                self.__filter_cond.append(getattr(self.repo, cond[0]) == cond[1])
            # ['or', 'id', 2] => WHERE id == 2 OR ...
            elif len(cond) is 3 and cond[0] == 'or':
                self.__filter_cond_or.append(getattr(self.repo, cond[1]) == cond[2])
            # ['id', '!=', 2] => WHERE id != 2
            elif len(cond) is 3 and cond[0] != 'or':
                if cond[1] == '!=':
                    self.__filter_cond.append(getattr(self.repo, cond[0]) != cond[2])
                elif cond[1] == '==':
                    self.__filter_cond.append(getattr(self.repo, cond[0]) == cond[2])
            # ['or', 'id', '==', 2] => WHERE id == 2 OR
            elif len(cond) is 4 and cond[0] == 'or':
                if cond[2] == '!=':
                    self.__filter_cond_or.append(getattr(self.repo, cond[1]) != cond[3])
                elif cond[2] == '==':
                    self.__filter_cond_or.append(getattr(self.repo, cond[1]) == cond[3])

        return query.filter(*self.__filter_cond).filter(or_(*self.__filter_cond_or))


class Repository(AbstractRepository):

    """Implementation of the AbstractRepository Interface.

    This implementation uses the SQLAlchemy ORM to implement the
    *Repository Design Pattern*. It uses the SQLAlchemy ``mapper`` function
    to map the Table Schema and the a Repository class. It also uses the
    ``listen`` method to hook up the before_* and after_* events.
    """

    def create(self):
        """Save the repository content in your data store.

        Returns:
            Repository: Self Instance
        """
        self.store.session.add(self)
        self.store.session.commit()

        return self

    def update(self):
        """Update the repository content in your data store.

        Returns:
            Repository: Self Instance.
        """
        self.store.session.commit()
        return self

    def delete(self):
        """Delete the repository content from your data store.

        Returns:
            Repository: Self Instance.
        """
        self.store.session.query(self.__class__).filter(self.__class__.id == self.id).delete()
        self.store.session.commit()
        return self

    @classmethod
    def get(cls, where=None):
        """Get all entries which satisfy a specific condition from your data store.

        Args:
            where (list, optional): Defaults to None. Where Condition

        Returns:
            list: List of items which satisfy the condition.
        """
        query = cls.store.session.query(cls)
        builder = QueryBuilder(cls, where)
        return builder.build(query)

    @classmethod
    def first(cls, where=None):
        """Get first entry which satisfy a specific condition from your data store.

        Args:
            where (list, optional): Defaults to None. Where Condition

        Returns:
            AbstractRepository: Item which satisfies the condition.
        """
        return cls.get(where).first()

    @classmethod
    def find(cls, id):
        """Find an entry of this repository based on its id.

        Args:
            id (int): ID to search for.

        Returns:
            AbstractRepository: Item which the concrete id
        """
        return cls.first(where=['id', id])

    @classmethod
    def all(cls):
        """Get all entries for this specific repository from your data store.

        Returns:
            list: List of all entires
        """
        return cls.store.session.query(cls).all()

    @staticmethod
    def mapping(cls, store):
        """Map data store content to repository classes.

        Example:
        Map a *User* Table in the data store to the *UserRepository*,
        which reflects the attributes of the User Table schema::

            Repository.mapping(UserRepository, store)

        Args:
            cls (AbstractRepository): Repository to map
            store (AbstractStore): Storage that is use
        """
        # set store
        cls.store = store

        # Map classes with relationships
        try:
            relationships = {}
            for key, relation in cls.__relationships__.items():
                if len(relation) is 2:
                    relationships[key] = relationship(relation[0], **relation[1])
                else:
                    relationships[key] = relationship(relation[0])

                # recursively map relations first otherwise it won't work!
                Repository.mapping(relation[0], store)

            Repository.map_to_table(
                cls, cls, cls.store.meta.tables.get(cls.__table__), properties=relationships
            )
        except Exception:
            logging.getLogger('experimentum').warning('Could not map table: ' + cls.__table__)

        # Listen to events
        listen(cls, 'before_insert', lambda m, conn, target: target.before_insert())
        listen(cls, 'after_insert', lambda m, conn, target: target.after_insert())
        listen(cls, 'before_update', lambda m, conn, target: target.before_update())
        listen(cls, 'after_update', lambda m, conn, target: target.after_update())

    @staticmethod
    def map_to_table(cls, repo, table, properties):
        """Get the SQLAlchemy mapper, i.e. map the tables to classes.

        Args:
            repo (Repository): Repository to map
            table (sqlalchemy.schema.table): Table to map
            properties (object): relationships to map
        """
        mapper(repo, table, properties=properties)

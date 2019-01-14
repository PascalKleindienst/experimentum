
class FooRepository(object):
    _mapped = False

    @staticmethod
    def mapping(cls, store):
        cls._mapped = True

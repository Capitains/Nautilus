from MyCapytain.resolvers.prototypes import Resolver
from abc import abstractmethod


class NautilusPrototypeResolver(Resolver):
    @abstractmethod
    def clear(self):
        """ Clear the cache of the current resolver
        """
        raise NotImplementedError()

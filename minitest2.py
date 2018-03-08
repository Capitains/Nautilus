from capitains_nautilus.cts.resolver import SparqlAlchemyNautilusCTSResolver
from capitains_nautilus.cts.resolver import NautilusCTSResolver
from MyCapytain.common.constants import Mimetypes
from time import time

timeit = 100

resolver = NautilusCTSResolver(["./tests/testing_data/latinLit2"])
resolver.parse()
print("Parsed 2")

current = time()
for _ in range(timeit):
    z = resolver.getMetadata().export(Mimetypes.XML.CTS)
now = time()

print("{timeit} operations in {sub} : {opsec} op / sec".format(
    timeit=timeit,
    sub=now-current,
    opsec=(now-current)/timeit
))

print(z)
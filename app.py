# For test purposes
from capitains_nautilus.flask_ext import FlaskNautilus
from capitains_nautilus.cts.resolver import NautilusCtsResolver
from flask import Flask


resolver = NautilusCtsResolver(["./tests/testing_data/latinLit2"])
resolver.parse()

app = Flask("Nautilus")
nautilus = FlaskNautilus(
    app=app,
    resolver=resolver
)

app.debug = True
app.run("0.0.0.0", 5000)

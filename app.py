# For test purposes
from capitains_nautilus.flask_ext import WerkzeugCacheWrapper, FlaskNautilus
from flask import Flask
from werkzeug.contrib.cache import NullCache
nautilus_cache = WerkzeugCacheWrapper(NullCache())
app = Flask("Nautilus")
nautilus = FlaskNautilus(
    app=app,
    resources=["./tests/test_data/latinLit"],
    parser_cache=nautilus_cache
)

app.debug = True
app.run("0.0.0.0", 5000)

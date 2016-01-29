from nautilus.flask_ext import FlaskNautilus
from werkzeug.contrib.cache import FileSystemCache
from flask import Flask

nautilus_cache = FileSystemCache("cache_dir")
app = Flask("Nautilus")
nautilus = FlaskNautilus(
    app=app,
    resources=["/home/thibault/dev/canonicals/canonical-latinLit"],
    parser_cache=nautilus_cache
)
app.run(debug=True)
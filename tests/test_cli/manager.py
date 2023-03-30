import sys
import os
sys.path.append(os.path.realpath(os.path.dirname(__file__) + "/../.."))

from tests.test_cli.app import resolver, nautilus
from capitains_nautilus.manager import FlaskNautilusManager

manager = FlaskNautilusManager(resolver, nautilus)

if __name__ == "__main__":
    manager()

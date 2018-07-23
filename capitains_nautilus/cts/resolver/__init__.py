from .base import NautilusCtsResolver
import logging

import_logger = logging.getLogger(__name__)

try:
    import bsddb3
    from ._berkeley_db import SleepyCatCtsResolver
except ImportError as e:
    import_logger.debug("BerkeleyDB is not installed. Its Nautilus SleepyCat implementation is not available")

try:
    import sqlalchemy
    from ._sql_alchemy import SparqlAlchemyNautilusCtsResolver
except ImportError as e:
    import_logger.debug("SQLAlchemy is not installed. Its Nautilus Sparql implementation is not available")


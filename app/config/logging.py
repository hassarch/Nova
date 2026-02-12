import logging

# Suppress SQLAlchemy logging entirely
logging.getLogger('sqlalchemy.engine').setLevel(logging.CRITICAL)
logging.getLogger('sqlalchemy.pool').setLevel(logging.CRITICAL)

# Get logger for the app
logger = logging.getLogger(__name__)

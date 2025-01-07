"""
Base class for SQLAlchemy models.
"""

# packages
import sqlalchemy.orm
import sqlalchemy.ext.declarative

# base factory
Base = sqlalchemy.ext.declarative.declarative_base()

# sqlalchemy.orm.registry
mapper_registry = sqlalchemy.orm.registry()

"""Base factory configuration for polyfactory."""

from faker import Faker
from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory

from app.base.models import BaseDBModel


class BaseFactory(SQLAlchemyFactory[BaseDBModel]):
    """Base factory for all database models."""

    __is_base_factory__ = True
    __faker__ = Faker()
    __session__ = None  # Will be set at runtime
    __check_model__ = False
    __set_relationships__ = False
    __set_association_proxy__ = False

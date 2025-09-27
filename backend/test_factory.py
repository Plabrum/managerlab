#!/usr/bin/env python3
"""Test script to understand polyfactory API."""

from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory
from polyfactory import Use
from faker import Faker

# Import our models
from app.brands.models.brands import Brand
from app.brands.models.contacts import BrandContact

fake = Faker()


class BrandFactory(SQLAlchemyFactory[Brand]):
    __model__ = Brand
    __faker__ = fake

    name = Use(fake.company)
    description = Use(fake.text, max_nb_chars=500)


class BrandContactFactory(SQLAlchemyFactory[BrandContact]):
    __model__ = BrandContact
    __faker__ = fake

    first_name = Use(fake.first_name)
    last_name = Use(fake.last_name)
    email = Use(fake.email)
    phone = Use(fake.phone_number)
    notes = Use(fake.text, max_nb_chars=150)


def test_basic_factory():
    """Test basic factory creation."""
    brand = BrandFactory.build()
    print(f"Brand: {brand.name}")
    print(f"Description: {brand.description[:50]}...")

    contact = BrandContactFactory.build()
    print(f"Contact: {contact.first_name} {contact.last_name}")
    print(f"Email: {contact.email}")


if __name__ == "__main__":
    test_basic_factory()

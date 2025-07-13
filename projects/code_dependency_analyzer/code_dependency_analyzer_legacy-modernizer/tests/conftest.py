"""Pytest configuration and fixtures."""

import tempfile
from pathlib import Path
import pytest


@pytest.fixture
def temp_codebase():
    """Create a temporary directory with sample Python files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create sample legacy codebase structure
        base_path = Path(tmpdir)

        # Create directories
        (base_path / "legacy_app").mkdir()
        (base_path / "legacy_app" / "models").mkdir()
        (base_path / "legacy_app" / "services").mkdir()
        (base_path / "legacy_app" / "utils").mkdir()

        # Create sample files
        _create_sample_files(base_path)

        yield str(base_path)


def _create_sample_files(base_path: Path):
    """Create sample Python files for testing."""

    # God class example
    (base_path / "legacy_app" / "models" / "user.py").write_text("""
class User:
    def __init__(self):
        self.db = None
        
    def create_user(self, name, email): pass
    def update_user(self, id, data): pass
    def delete_user(self, id): pass
    def get_user(self, id): pass
    def list_users(self): pass
    def validate_email(self, email): pass
    def send_email(self, to, subject, body): pass
    def hash_password(self, password): pass
    def verify_password(self, password, hash): pass
    def generate_token(self, user_id): pass
    def verify_token(self, token): pass
    def log_activity(self, user_id, action): pass
    def get_activity_log(self, user_id): pass
    def export_to_csv(self, users): pass
    def import_from_csv(self, file): pass
    def calculate_age(self, birthdate): pass
    def format_name(self, first, last): pass
    def check_permissions(self, user_id, resource): pass
    def grant_permission(self, user_id, permission): pass
    def revoke_permission(self, user_id, permission): pass
    def get_user_stats(self, user_id): pass
    def update_last_login(self, user_id): pass
    def reset_password(self, email): pass
    def change_password(self, user_id, old_pwd, new_pwd): pass
    def deactivate_account(self, user_id): pass
    def reactivate_account(self, user_id): pass
    def merge_accounts(self, user_id1, user_id2): pass
    def get_user_preferences(self, user_id): pass
    def update_preferences(self, user_id, prefs): pass
""")

    # Circular dependency example
    (base_path / "legacy_app" / "services" / "order_service.py").write_text("""
from ..services.payment_service import PaymentService
from ..models.user import User

class OrderService:
    def __init__(self):
        self.payment_service = PaymentService()
        
    def create_order(self, user_id, items):
        # Complex order logic
        pass
""")

    (base_path / "legacy_app" / "services" / "payment_service.py").write_text("""
from ..services.order_service import OrderService

class PaymentService:
    def process_payment(self, order_id):
        # Circular dependency
        order_service = OrderService()
        pass
""")

    # Database coupling example
    (base_path / "legacy_app" / "models" / "product.py").write_text("""
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Product(Base):
    __tablename__ = 'products'
    
    def get_products(self):
        query = "SELECT * FROM products WHERE active = 1"
        return self.execute_query(query)
        
    def update_inventory(self, product_id, quantity):
        query = f"UPDATE products SET quantity = {quantity} WHERE id = {product_id}"
        self.execute_query(query)
""")

    # Another module accessing same table
    (base_path / "legacy_app" / "services" / "inventory_service.py").write_text("""
class InventoryService:
    def check_stock(self, product_id):
        query = f"SELECT quantity FROM products WHERE id = {product_id}"
        return self.execute_query(query)
        
    def update_stock(self, product_id, delta):
        query = f"UPDATE products SET quantity = quantity + {delta} WHERE id = {product_id}"
        self.execute_query(query)
""")

    # Spaghetti dependencies
    (base_path / "legacy_app" / "utils" / "helpers.py").write_text("""
import os
import sys
import json
import csv
import datetime
import logging
import requests
import numpy
import pandas
import sqlalchemy
import redis
import celery
import boto3
import stripe
import twilio
import sendgrid
import slack_sdk
import jira
import confluence
import elasticsearch

def do_everything():
    # Function with too many dependencies
    pass
""")

    # Feature envy example
    (base_path / "legacy_app" / "services" / "report_generator.py").write_text("""
from ..models.user import User
from ..models.user import User as UserModel
from ..models.user import User as UserClass
from ..models.user import hash_password
from ..models.user import verify_password
from ..models.user import generate_token

class ReportGenerator:
    def generate_user_report(self):
        # Too many dependencies on User module
        pass
""")

    # Monolithic __init__ file
    (base_path / "legacy_app" / "__init__.py").write_text(
        """
# Monolithic application with everything in one place
"""
        + "\n".join([f"def function_{i}(): pass" for i in range(100)])
    )


@pytest.fixture
def sample_patterns():
    """Sample legacy patterns for testing."""
    from legacy_analyzer.models import (
        LegacyPattern,
        PatternType,
        ModernizationDifficulty,
        RiskLevel,
    )

    return [
        LegacyPattern(
            pattern_type=PatternType.GOD_CLASS,
            module_path="models/user.py",
            description="Large class with too many responsibilities",
            difficulty=ModernizationDifficulty.HIGH,
            risk=RiskLevel.HIGH,
            affected_files=["models/user.py"],
            dependencies=["db", "email", "crypto"],
            metrics={"methods": 30, "lines": 500},
        ),
        LegacyPattern(
            pattern_type=PatternType.CIRCULAR_DEPENDENCY,
            module_path="services/order_service.py",
            description="Circular dependency between services",
            difficulty=ModernizationDifficulty.CRITICAL,
            risk=RiskLevel.CRITICAL,
            affected_files=["services/order_service.py", "services/payment_service.py"],
            dependencies=["services/payment_service", "services/order_service"],
        ),
    ]


@pytest.fixture
def sample_database_couplings():
    """Sample database couplings for testing."""
    from legacy_analyzer.models import DatabaseCoupling

    return [
        DatabaseCoupling(
            coupled_modules=["models/product.py", "services/inventory_service.py"],
            shared_tables=["products"],
            orm_models=["Product"],
            raw_sql_queries=["SELECT * FROM products", "UPDATE products SET quantity"],
            coupling_strength=0.8,
            decoupling_effort_hours=40,
        )
    ]

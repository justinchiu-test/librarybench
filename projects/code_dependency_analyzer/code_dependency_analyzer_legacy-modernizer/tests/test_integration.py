"""Integration tests for the complete system."""

import tempfile
from pathlib import Path
from legacy_analyzer import LegacyAnalyzer


class TestIntegration:
    """Integration tests for real-world scenarios."""

    def test_20_year_old_erp_system(self):
        """Test analyzing a simulated 20-year-old monolithic ERP system."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)

            # Create ERP-like structure
            modules = ["accounting", "inventory", "hr", "sales", "reporting"]
            for module in modules:
                module_path = base_path / module
                module_path.mkdir()

                # Create god class
                (module_path / f"{module}_manager.py").write_text(
                    f"""
class {module.title()}Manager:
    def __init__(self):
        self.db = DatabaseConnection()
        
    # 30+ methods simulating god class
"""
                    + "\n".join([f"    def method_{i}(self): pass" for i in range(35)])
                )

                # Create tightly coupled service
                (module_path / f"{module}_service.py").write_text(f"""
from ..accounting.accounting_manager import AccountingManager
from ..inventory.inventory_manager import InventoryManager
from ..hr.hr_manager import HRManager
import mysql.connector

class {module.title()}Service:
    def process(self):
        # Multiple SQL queries to trigger detection
        # All services access shared tables
        query1 = "SELECT * FROM company_data WHERE module = '{module}'"
        query2 = "UPDATE company_data SET last_accessed = NOW() WHERE module = '{module}'"
        query3 = "SELECT * FROM audit_log WHERE module = '{module}'"
        self.db.execute(query1)
        self.db.execute(query2)
        self.db.execute(query3)
""")

            # Analyze the ERP system
            analyzer = LegacyAnalyzer()
            result = analyzer.analyze_codebase(str(base_path))

            # Should identify multiple god classes
            god_classes = [
                p for p in result.legacy_patterns if p.pattern_type.value == "god_class"
            ]
            assert len(god_classes) >= len(modules)

            # Should identify database coupling
            assert len(result.database_couplings) > 0

            # Should generate comprehensive roadmap
            assert result.modernization_roadmap is not None
            assert len(result.modernization_roadmap.phases) >= 3

    def test_legacy_ecommerce_platform(self):
        """Test planning strangler fig for a legacy e-commerce platform."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)

            # Create e-commerce structure
            components = {
                "catalog": ["product.py", "category.py", "search.py"],
                "cart": ["cart.py", "checkout.py", "payment.py"],
                "user": ["authentication.py", "profile.py", "orders.py"],
                "admin": ["dashboard.py", "reports.py", "settings.py"],
            }

            for component, files in components.items():
                comp_path = base_path / component
                comp_path.mkdir()

                for file in files:
                    # Create interconnected modules
                    class_name = file.replace(".py", "").title()
                    # Only import from other components, not same component
                    imports = []
                    if component != "cart":
                        imports.append("from ..cart.cart import Cart")
                    if component != "user":
                        imports.append(
                            "from ..user.authentication import Authentication"
                        )
                    if component != "catalog":
                        imports.append("from ..catalog.product import Product")

                    import_statements = "\n".join(imports) if imports else ""

                    (comp_path / file).write_text(f"""
{import_statements}

class {class_name}:
    def __init__(self):
        pass
""")

            # Analyze for strangler fig boundaries
            analyzer = LegacyAnalyzer()
            result = analyzer.analyze_codebase(str(base_path))

            # Should identify boundaries
            assert len(result.strangler_boundaries) > 0

            # Should find high-isolation boundaries
            high_isolation = [
                b for b in result.strangler_boundaries if b.isolation_score > 0.5
            ]
            assert len(high_isolation) > 0

            # Boundaries should have reasonable effort estimates
            for boundary in result.strangler_boundaries:
                assert boundary.estimated_effort_hours > 0
                assert boundary.recommended_order > 0

    def test_extracting_authentication_system(self):
        """Test extracting authentication from a tightly coupled system."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)

            # Create tightly coupled authentication
            (base_path / "auth.py").write_text("""
from database import db
from cache import redis_client
from messaging import email_service
from logging import audit_logger
from config import settings
from user_service import UserService  # Circular dependency!

class AuthenticationService:
    def __init__(self):
        self.db = db
        self.cache = redis_client
        self.email = email_service
        self.logger = audit_logger
        self.user_service = None  # Will create circular reference
        
    def login(self, username, password):
        user_query = f"SELECT * FROM users WHERE username = '{username}'"
        user = self.db.execute(user_query)
        
        session_query = f"INSERT INTO sessions (user_id) VALUES ({user.id})"
        self.db.execute(session_query)
        
        self.cache.set(f"session:{user.id}", user.data)
        self.logger.log(f"User {username} logged in")
        
    def logout(self, user_id):
        delete_query = f"DELETE FROM sessions WHERE user_id = {user_id}"
        self.db.execute(delete_query)
""")

            # Create dependent modules
            (base_path / "user_service.py").write_text("""
from auth import AuthenticationService

class UserService:
    def __init__(self):
        self.auth = AuthenticationService()
        
    def create_user(self, data):
        # Depends on auth
        self.auth.login("user", "pass")
        
    def get_user_auth(self):
        return self.auth
""")

            (base_path / "api_gateway.py").write_text("""
from auth import AuthenticationService

class APIGateway:
    def __init__(self):
        self.auth = AuthenticationService()
        
    def handle_request(self, request):
        # Uses auth for every request
        pass
""")

            # Create dummy imports
            for module in ["database", "cache", "messaging", "logging", "config"]:
                (base_path / f"{module}.py").write_text(f"{module} = None")

            # Analyze extraction feasibility
            analyzer = LegacyAnalyzer()
            result = analyzer.analyze_codebase(
                str(base_path), modules_to_extract=["auth.py"]
            )

            # Should analyze auth module
            auth_feasibility = next(
                (f for f in result.extraction_feasibilities if "auth" in f.module_path),
                None,
            )
            assert auth_feasibility is not None

            # Should identify dependencies to break
            assert len(auth_feasibility.dependencies_to_break) > 0

            # Should identify backward compatibility needs
            assert len(auth_feasibility.backward_compatibility_requirements) > 0

            # Should provide recommendations
            assert len(auth_feasibility.recommendations) > 0

    def test_shared_database_dependencies(self):
        """Test identifying shared database dependencies in multi-tenant app."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)

            # Create multi-tenant modules
            tenants = ["tenant_manager", "billing", "usage_tracker", "provisioning"]

            for tenant_module in tenants:
                # Using triple quotes with escaped braces to avoid f-string conflicts
                module_content = f"""
import sqlalchemy
from sqlalchemy import create_engine

class {tenant_module.title().replace("_", "")}:
    __tablename__ = 'tenants'
    
    def get_tenant(self, tenant_id):
        return self.execute("SELECT * FROM tenants WHERE id = %s", tenant_id)
        
    def update_tenant(self, tenant_id, data):
        query = "UPDATE tenants SET data = '{{}}' WHERE id = {{}}".format(data, tenant_id)
        self.execute(query)
        
    def check_limits(self, tenant_id):
        usage_query = "SELECT * FROM tenant_usage WHERE tenant_id = {{}}".format(tenant_id)
        limits_query = "SELECT * FROM tenant_limits WHERE tenant_id = {{}}".format(tenant_id)
"""
                (base_path / f"{tenant_module}.py").write_text(module_content)

            # Analyze database coupling
            analyzer = LegacyAnalyzer()
            result = analyzer.analyze_codebase(str(base_path))

            # Should identify shared table access
            tenant_couplings = [
                c for c in result.database_couplings if "tenants" in c.shared_tables
            ]
            assert len(tenant_couplings) > 0

            # Should find all modules accessing tenants table
            coupled_modules = tenant_couplings[0].coupled_modules
            assert len(coupled_modules) >= 3

            # Should identify raw SQL
            assert any(c.raw_sql_queries for c in result.database_couplings)

    def test_two_year_modernization_roadmap(self):
        """Test creating a 2-year modernization roadmap for a financial system."""
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir)

            # Create financial system structure
            systems = {
                "core_banking": ["accounts", "transactions", "ledger"],
                "risk_management": ["credit_scoring", "fraud_detection", "compliance"],
                "reporting": ["regulatory", "internal", "customer"],
                "integration": ["payment_gateways", "third_party", "apis"],
            }

            for system, modules in systems.items():
                system_path = base_path / system
                system_path.mkdir()

                for module in modules:
                    # Create complex interdependencies
                    (system_path / f"{module}.py").write_text(
                        f"""
# Simulating legacy financial code
from core_banking.accounts import AccountManager
from risk_management.compliance import ComplianceChecker
import cx_Oracle

class {module.title().replace("_", "")}:
    def __init__(self):
        self.db = cx_Oracle.connect('legacy/system@oracle')
        
    def process_transaction(self, data):
        # Complex business logic with raw SQL
        query = '''
        BEGIN
            UPDATE accounts SET balance = balance - :amount WHERE id = :from_id;
            UPDATE accounts SET balance = balance + :amount WHERE id = :to_id;
            INSERT INTO audit_log VALUES (:transaction_id, SYSDATE);
        END;
        '''
        self.db.execute(query, data)
"""
                        + "\n".join(
                            [
                                f"    def legacy_method_{i}(self): pass"
                                for i in range(15)
                            ]
                        )
                    )

            # Analyze and generate roadmap
            analyzer = LegacyAnalyzer()
            result = analyzer.analyze_codebase(str(base_path))

            # Should generate comprehensive roadmap
            roadmap = result.modernization_roadmap
            assert roadmap is not None

            # Should span approximately 2 years (730 days)
            assert 500 <= roadmap.total_duration_days <= 1000

            # Should have multiple phases
            assert len(roadmap.phases) >= 4

            # Should identify critical risks
            assert "Database Coupling" in roadmap.risk_assessment

            # Should have realistic success metrics
            assert roadmap.success_metrics["risk_reduction_potential"] >= 40

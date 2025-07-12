"""Tests for database coupling detection."""

from legacy_analyzer.database_coupling_detector import DatabaseCouplingDetector


class TestDatabaseCouplingDetector:
    """Test database coupling detection functionality."""

    def test_detect_shared_tables(self, temp_codebase):
        """Test detection of shared table access."""
        detector = DatabaseCouplingDetector()
        couplings = detector.analyze_database_coupling(temp_codebase)

        assert len(couplings) > 0

        # Find coupling for products table
        product_coupling = next(
            (c for c in couplings if "products" in c.shared_tables), None
        )

        assert product_coupling is not None
        assert len(product_coupling.coupled_modules) >= 2
        assert any("product.py" in m for m in product_coupling.coupled_modules)
        assert any(
            "inventory_service.py" in m for m in product_coupling.coupled_modules
        )

    def test_detect_raw_sql_queries(self, temp_codebase):
        """Test detection of raw SQL queries."""
        detector = DatabaseCouplingDetector()
        couplings = detector.analyze_database_coupling(temp_codebase)

        # Find couplings with raw SQL
        sql_couplings = [c for c in couplings if c.raw_sql_queries]

        assert len(sql_couplings) > 0

        # Check that SQL queries were detected
        all_queries = []
        for coupling in sql_couplings:
            all_queries.extend(coupling.raw_sql_queries)

        assert any("SELECT" in q for q in all_queries)
        assert any("UPDATE" in q for q in all_queries)
        assert any("products" in q for q in all_queries)

    def test_coupling_strength_calculation(self, temp_codebase):
        """Test coupling strength calculation."""
        detector = DatabaseCouplingDetector()
        couplings = detector.analyze_database_coupling(temp_codebase)

        for coupling in couplings:
            # Coupling strength should be between 0 and 1
            assert 0 <= coupling.coupling_strength <= 1

            # Higher coupling for more modules
            if len(coupling.coupled_modules) > 2:
                assert coupling.coupling_strength > 0.2

    def test_decoupling_effort_estimation(self, temp_codebase):
        """Test decoupling effort estimation."""
        detector = DatabaseCouplingDetector()
        couplings = detector.analyze_database_coupling(temp_codebase)

        for coupling in couplings:
            # Effort should be positive
            assert coupling.decoupling_effort_hours > 0

            # More effort for more coupled modules
            if len(coupling.coupled_modules) > 2:
                assert coupling.decoupling_effort_hours > 20

            # More effort for raw SQL
            if coupling.raw_sql_queries:
                assert coupling.decoupling_effort_hours > 10

    def test_orm_detection(self, temp_codebase):
        """Test ORM usage detection."""
        detector = DatabaseCouplingDetector()
        couplings = detector.analyze_database_coupling(temp_codebase)

        # Check that we detected ORM usage
        assert any(
            "sqlalchemy" in detector.module_db_access[m]
            for m in detector.module_db_access
        )

        # Check that we found the Product model
        assert any(
            "Product" in models for models in detector.module_orm_models.values()
        )

    def test_table_name_extraction(self, temp_codebase):
        """Test table name extraction from various sources."""
        detector = DatabaseCouplingDetector()
        couplings = detector.analyze_database_coupling(temp_codebase)

        # Check that we found the products table
        all_tables = set()
        for tables in detector.module_tables.values():
            all_tables.update(tables)

        assert "products" in all_tables

    def test_empty_codebase(self, tmp_path):
        """Test handling of codebase without database access."""
        detector = DatabaseCouplingDetector()
        couplings = detector.analyze_database_coupling(str(tmp_path))

        assert isinstance(couplings, list)
        assert len(couplings) == 0

    def test_multiple_table_coupling(self, tmp_path):
        """Test detection of modules accessing multiple tables."""
        # Create test file with multiple table access
        test_file = tmp_path / "multi_table.py"
        test_file.write_text("""
class DataService:
    def get_user_orders(self, user_id):
        users_query = f"SELECT * FROM users WHERE id = {user_id}"
        orders_query = f"SELECT * FROM orders WHERE user_id = {user_id}"
        products_query = "SELECT * FROM products WHERE id IN (...)"
        
    def update_inventory(self):
        update_products = "UPDATE products SET quantity = quantity - 1"
        update_inventory = "UPDATE inventory SET last_modified = NOW()"
""")

        detector = DatabaseCouplingDetector()
        couplings = detector.analyze_database_coupling(str(tmp_path))

        # Should detect multiple tables
        assert "users" in detector.module_tables.get("multi_table.py", set())
        assert "orders" in detector.module_tables.get("multi_table.py", set())
        assert "products" in detector.module_tables.get("multi_table.py", set())

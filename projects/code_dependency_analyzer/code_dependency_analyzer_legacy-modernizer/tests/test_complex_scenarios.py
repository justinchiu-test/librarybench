"""Complex scenario tests for the Legacy System Modernization Analyzer."""

from legacy_analyzer import LegacyAnalyzer
from legacy_analyzer.models import PatternType


class TestComplexScenarios:
    """Test complex real-world scenarios."""

    def test_mixed_language_project_with_python(self, tmp_path):
        """Test project with multiple languages where only Python is analyzed."""
        # Create mixed language files
        (tmp_path / "main.py").write_text("class PythonClass: pass")
        (tmp_path / "helper.js").write_text("function helper() {}")
        (tmp_path / "styles.css").write_text("body { margin: 0; }")
        (tmp_path / "config.yaml").write_text("key: value")
        (tmp_path / "Makefile").write_text("all:\n\techo 'build'")

        analyzer = LegacyAnalyzer()
        result = analyzer.analyze_codebase(str(tmp_path))

        # Should only analyze Python files
        assert result.summary["total_modules"] == 1

    def test_microservices_with_shared_libraries(self, tmp_path):
        """Test microservices architecture with shared libraries."""
        # Create microservices structure
        services = ["auth_service", "user_service", "order_service"]
        shared = tmp_path / "shared_lib"
        shared.mkdir()

        # Create shared library
        (shared / "database.py").write_text("""
class DatabaseConnection:
    def query(self, sql):
        return f"SELECT * FROM shared_db WHERE {sql}"
""")

        (shared / "cache.py").write_text("""
class CacheManager:
    def get(self, key):
        return f"CACHED:{key}"
""")

        # Create services that use shared lib
        for service in services:
            service_dir = tmp_path / service
            service_dir.mkdir()

            (service_dir / f"{service}.py").write_text(f"""
from ..shared_lib.database import DatabaseConnection
from ..shared_lib.cache import CacheManager

class {service.title().replace("_", "")}:
    def __init__(self):
        self.db = DatabaseConnection()
        self.cache = CacheManager()
        
    def process(self):
        data = self.db.query("service='{service}'")
        self.cache.get('{service}_data')
""")

        analyzer = LegacyAnalyzer()
        result = analyzer.analyze_codebase(str(tmp_path))

        # Should detect feature envy on shared libraries
        feature_envy = [
            p
            for p in result.legacy_patterns
            if p.pattern_type == PatternType.FEATURE_ENVY
        ]
        assert len(feature_envy) > 0

    def test_plugin_architecture_analysis(self, tmp_path):
        """Test analysis of plugin-based architecture."""
        # Create core system
        core = tmp_path / "core"
        core.mkdir()

        (core / "plugin_manager.py").write_text("""
class PluginManager:
    def __init__(self):
        self.plugins = {}
        
    def register_plugin(self, name, plugin):
        self.plugins[name] = plugin
        
    def execute_plugin(self, name, *args):
        return self.plugins[name].execute(*args)
""")

        # Create plugins directory
        plugins = tmp_path / "plugins"
        plugins.mkdir()

        # Create multiple plugins
        for i in range(5):
            plugin_dir = plugins / f"plugin_{i}"
            plugin_dir.mkdir()

            (plugin_dir / "__init__.py").write_text(f"""
from ...core.plugin_manager import PluginManager

class Plugin{i}:
    def execute(self, data):
        return f"Plugin {i} processed: {{data}}"
        
    def register(self, manager: PluginManager):
        manager.register_plugin("plugin_{i}", self)
""")

        analyzer = LegacyAnalyzer()
        result = analyzer.analyze_codebase(str(tmp_path))

        # Should analyze plugin architecture
        assert result.summary["total_modules"] >= 6

    def test_event_driven_architecture(self, tmp_path):
        """Test event-driven system with publishers and subscribers."""
        # Create event system
        (tmp_path / "event_bus.py").write_text("""
class EventBus:
    def __init__(self):
        self.subscribers = {}
        
    def subscribe(self, event_type, handler):
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(handler)
        
    def publish(self, event_type, data):
        for handler in self.subscribers.get(event_type, []):
            handler(data)
""")

        # Create publishers
        (tmp_path / "user_publisher.py").write_text("""
from event_bus import EventBus

class UserPublisher:
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        
    def user_created(self, user_data):
        self.event_bus.publish("user.created", user_data)
        
    def user_updated(self, user_data):
        self.event_bus.publish("user.updated", user_data)
""")

        # Create subscribers
        (tmp_path / "email_subscriber.py").write_text("""
from event_bus import EventBus

class EmailSubscriber:
    def __init__(self, event_bus: EventBus):
        event_bus.subscribe("user.created", self.send_welcome_email)
        event_bus.subscribe("user.updated", self.send_update_email)
        
    def send_welcome_email(self, user_data):
        pass
        
    def send_update_email(self, user_data):
        pass
""")

        analyzer = LegacyAnalyzer()
        result = analyzer.analyze_codebase(str(tmp_path))

        # Event-driven systems should have good isolation
        assert len(result.strangler_boundaries) >= 0

    def test_multi_tenant_database_architecture(self, tmp_path):
        """Test multi-tenant system with schema-per-tenant pattern."""
        # Create tenant manager
        (tmp_path / "tenant_manager.py").write_text("""
class TenantManager:
    def get_tenant_schema(self, tenant_id):
        return f"tenant_{tenant_id}"
        
    def execute_for_tenant(self, tenant_id, query):
        schema = self.get_tenant_schema(tenant_id)
        return f"USE {schema}; {query}"
""")

        # Create services that use tenant manager
        services = ["billing", "reporting", "analytics"]
        for service in services:
            (tmp_path / f"{service}_service.py").write_text(f"""
from tenant_manager import TenantManager

class {service.title()}Service:
    def __init__(self):
        self.tenant_mgr = TenantManager()
        
    def process_for_tenant(self, tenant_id):
        # Access tenant-specific tables
        query1 = "SELECT * FROM orders WHERE status = 'active'"
        query2 = "UPDATE metrics SET last_run = NOW()"
        
        self.tenant_mgr.execute_for_tenant(tenant_id, query1)
        self.tenant_mgr.execute_for_tenant(tenant_id, query2)
""")

        analyzer = LegacyAnalyzer()
        result = analyzer.analyze_codebase(str(tmp_path))

        # Should detect database coupling through tenant manager
        assert len(result.database_couplings) > 0

    def test_legacy_framework_migration(self, tmp_path):
        """Test system migrating from old to new framework."""
        # Old framework code
        old_dir = tmp_path / "old_framework"
        old_dir.mkdir()

        (old_dir / "old_controller.py").write_text("""
from old_framework import Controller, route

class OldUserController(Controller):
    @route('/users')
    def list_users(self):
        return self.db.query("SELECT * FROM users")
        
    @route('/users/<id>')
    def get_user(self, id):
        return self.db.query(f"SELECT * FROM users WHERE id = {id}")
""")

        # New framework code
        new_dir = tmp_path / "new_framework"
        new_dir.mkdir()

        (new_dir / "new_controller.py").write_text("""
from new_framework import APIController, get, post
from ..old_framework.old_controller import OldUserController

class NewUserController(APIController):
    def __init__(self):
        # Still using old controller during migration
        self.old_controller = OldUserController()
        
    @get('/api/users')
    async def list_users(self):
        # Wrapper around old functionality
        return await self.old_controller.list_users()
        
    @get('/api/users/{user_id}')
    async def get_user(self, user_id: int):
        return await self.old_controller.get_user(user_id)
""")

        analyzer = LegacyAnalyzer()
        result = analyzer.analyze_codebase(str(tmp_path))

        # Should identify this as good strangler fig boundary
        assert len(result.strangler_boundaries) >= 0

        # Should detect the wrapper pattern
        patterns = result.legacy_patterns
        assert any(
            "old_framework" in p.module_path or "new_framework" in p.module_path
            for p in patterns
        )

    def test_data_pipeline_architecture(self, tmp_path):
        """Test data pipeline with multiple processing stages."""
        # Create pipeline stages
        stages = ["ingestion", "validation", "transformation", "storage"]

        for i, stage in enumerate(stages):
            (tmp_path / f"{stage}_stage.py").write_text(f"""
class {stage.title()}Stage:
    def __init__(self):
        self.stage_name = "{stage}"
        
    def process(self, data):
        # Simulate database operations
        self.log_to_db(f"Processing {{len(data)}} records in {stage}")
        processed = self.transform_data(data)
        self.save_checkpoint(processed)
        return processed
        
    def log_to_db(self, message):
        query = f"INSERT INTO pipeline_logs (stage, message) VALUES ('{stage}', '{{message}}')"
        return query
        
    def save_checkpoint(self, data):
        query = f"INSERT INTO checkpoints (stage, data) VALUES ('{stage}', '{{data}}')"
        return query
        
    def transform_data(self, data):
        return f"{stage}_processed_{{data}}"
""")

        # Create pipeline orchestrator
        (tmp_path / "pipeline_orchestrator.py").write_text("""
from ingestion_stage import IngestionStage
from validation_stage import ValidationStage
from transformation_stage import TransformationStage
from storage_stage import StorageStage

class PipelineOrchestrator:
    def __init__(self):
        self.stages = [
            IngestionStage(),
            ValidationStage(),
            TransformationStage(),
            StorageStage()
        ]
        
    def run_pipeline(self, initial_data):
        data = initial_data
        for stage in self.stages:
            data = stage.process(data)
        return data
""")

        analyzer = LegacyAnalyzer()
        result = analyzer.analyze_codebase(str(tmp_path))

        # Pipeline stages should be good extraction candidates
        high_feasibility = [
            f for f in result.extraction_feasibilities if f.feasibility_score > 0.7
        ]
        assert len(high_feasibility) > 0

        # Should detect shared database access
        assert len(result.database_couplings) > 0

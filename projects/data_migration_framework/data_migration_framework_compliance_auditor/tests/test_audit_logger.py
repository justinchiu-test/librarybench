"""Tests for the cryptographic audit logger."""

from datetime import datetime, timedelta
from freezegun import freeze_time
import pytz

from pymigrate.audit import AuditLogger, InMemoryAuditStorage
from pymigrate.audit.crypto import CryptoManager
from pymigrate.models import AuditEvent, OperationType


class TestAuditLogger:
    """Test suite for AuditLogger."""

    def test_log_event_creates_audit_trail(self):
        """Test that logging events creates an audit trail."""
        storage = InMemoryAuditStorage()
        logger = AuditLogger(storage, enable_signatures=False)

        # Log an event
        event = logger.log_event(
            actor="test_user",
            operation=OperationType.READ,
            resource="test_resource",
            details={"key": "value"},
        )

        # Verify event was created
        assert event.actor == "test_user"
        assert event.operation == OperationType.READ
        assert event.resource == "test_resource"
        assert event.details == {"key": "value"}
        assert event.hash is not None

        # Verify event was stored
        stored_event = storage.get_event(event.event_id)
        assert stored_event == event

    def test_hash_chain_integrity(self):
        """Test that events form a valid hash chain."""
        storage = InMemoryAuditStorage()
        logger = AuditLogger(storage, enable_signatures=False)

        # Log multiple events
        events = []
        for i in range(5):
            event = logger.log_event(
                actor=f"user_{i}",
                operation=OperationType.WRITE,
                resource=f"resource_{i}",
            )
            events.append(event)

        # Verify hash chain
        assert events[0].previous_hash is None
        for i in range(1, len(events)):
            assert events[i].previous_hash == events[i - 1].hash

        # Verify chain integrity
        assert logger.verify_chain_integrity()
        assert storage.verify_integrity()

    def test_event_signatures(self):
        """Test that events are properly signed and verified."""
        storage = InMemoryAuditStorage()
        crypto = CryptoManager()
        logger = AuditLogger(storage, crypto_manager=crypto, enable_signatures=True)

        # Log an event
        event = logger.log_event(
            actor="test_user",
            operation=OperationType.TRANSFORM,
            resource="sensitive_data",
        )

        # Verify signature exists
        assert event.signature is not None

        # Verify event
        assert logger.verify_event(event)

        # Tamper with event
        tampered_event = AuditEvent(
            event_id=event.event_id,
            timestamp=event.timestamp,
            actor="malicious_user",  # Changed
            operation=event.operation,
            resource=event.resource,
            details=event.details,
            previous_hash=event.previous_hash,
            hash=event.hash,
            signature=event.signature,
        )

        # Verification should fail
        assert not logger.verify_event(tampered_event)

    def test_timestamp_ordering(self):
        """Test that events maintain proper timestamp ordering."""
        storage = InMemoryAuditStorage()
        logger = AuditLogger(storage, enable_signatures=False)

        # Log events with specific timestamps
        base_time = datetime.now(pytz.UTC)

        with freeze_time(base_time):
            event1 = logger.log_event("user1", OperationType.READ, "resource1")

        with freeze_time(base_time + timedelta(minutes=5)):
            event2 = logger.log_event("user2", OperationType.WRITE, "resource2")

        # Verify timestamps
        assert event1.timestamp < event2.timestamp

        # Query by time range
        events = storage.get_events_by_timerange(
            base_time - timedelta(minutes=1), base_time + timedelta(minutes=3)
        )
        assert len(events) == 1
        assert events[0] == event1

    def test_actor_based_queries(self):
        """Test querying events by actor."""
        storage = InMemoryAuditStorage()
        logger = AuditLogger(storage, enable_signatures=False)

        # Log events for different actors
        logger.log_event("alice", OperationType.READ, "file1")
        logger.log_event("bob", OperationType.WRITE, "file2")
        logger.log_event("alice", OperationType.DELETE, "file3")

        # Query by actor
        alice_events = storage.get_events_by_actor("alice")
        assert len(alice_events) == 2
        assert all(e.actor == "alice" for e in alice_events)

        bob_events = storage.get_events_by_actor("bob")
        assert len(bob_events) == 1
        assert bob_events[0].actor == "bob"

    def test_resource_based_queries(self):
        """Test querying events by resource."""
        storage = InMemoryAuditStorage()
        logger = AuditLogger(storage, enable_signatures=False)

        # Log events for different resources
        logger.log_event("user1", OperationType.READ, "database:users")
        logger.log_event("user2", OperationType.WRITE, "database:users")
        logger.log_event("user3", OperationType.READ, "file:config.json")

        # Query by resource
        db_events = storage.get_events_by_resource("database:users")
        assert len(db_events) == 2
        assert all(e.resource == "database:users" for e in db_events)

    def test_tamper_detection(self):
        """Test detection of tampering in the audit log."""
        storage = InMemoryAuditStorage()
        logger = AuditLogger(storage, enable_signatures=False)

        # Log some events
        event1 = logger.log_event("user1", OperationType.READ, "resource1")
        event2 = logger.log_event("user2", OperationType.WRITE, "resource2")
        event3 = logger.log_event("user3", OperationType.DELETE, "resource3")

        # Verify initial integrity
        assert storage.verify_integrity()

        # Tamper with middle event
        storage._events[event2.event_id] = AuditEvent(
            event_id=event2.event_id,
            timestamp=event2.timestamp,
            actor="tampered_user",
            operation=event2.operation,
            resource=event2.resource,
            details=event2.details,
            previous_hash="wrong_hash",
            hash=event2.hash,
            signature=event2.signature,
        )

        # Integrity check should fail
        assert not storage.verify_integrity()

    def test_high_volume_performance(self):
        """Test performance with high volume of events."""
        storage = InMemoryAuditStorage()
        logger = AuditLogger(storage, enable_signatures=False)

        # Log many events
        start_time = datetime.now()
        num_events = 1000

        for i in range(num_events):
            logger.log_event(
                actor=f"user_{i % 10}",
                operation=OperationType.READ,
                resource=f"resource_{i % 50}",
                details={"index": i},
            )

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # Verify performance (should complete in reasonable time)
        assert duration < 10  # Should complete in less than 10 seconds

        # Verify all events were logged
        assert len(storage.get_all_events()) == num_events

        # Verify chain integrity
        assert storage.verify_integrity()

    def test_custom_timestamp(self):
        """Test logging events with custom timestamps."""
        storage = InMemoryAuditStorage()
        logger = AuditLogger(storage, enable_signatures=False)

        # Log event with custom timestamp
        custom_time = datetime(2023, 1, 1, 12, 0, 0, tzinfo=pytz.UTC)
        event = logger.log_event(
            actor="test_user",
            operation=OperationType.WRITE,
            resource="test_resource",
            timestamp=custom_time,
        )

        assert event.timestamp == custom_time

    def test_empty_details_handling(self):
        """Test handling of events with empty or no details."""
        storage = InMemoryAuditStorage()
        logger = AuditLogger(storage, enable_signatures=False)

        # Log event without details
        event1 = logger.log_event(
            actor="user1", operation=OperationType.READ, resource="resource1"
        )
        assert event1.details == {}

        # Log event with empty details
        event2 = logger.log_event(
            actor="user2",
            operation=OperationType.WRITE,
            resource="resource2",
            details={},
        )
        assert event2.details == {}


class TestCryptoManager:
    """Test suite for CryptoManager."""

    def test_key_generation(self):
        """Test RSA key pair generation."""
        crypto = CryptoManager()
        private_key, public_key = crypto.generate_key_pair()

        # Verify keys are generated
        assert private_key is not None
        assert public_key is not None
        assert (
            b"BEGIN RSA PRIVATE KEY" in private_key
            or b"BEGIN PRIVATE KEY" in private_key
        )
        assert b"BEGIN PUBLIC KEY" in public_key

    def test_data_signing_and_verification(self):
        """Test signing and verifying data."""
        crypto = CryptoManager()
        crypto.generate_key_pair()

        # Sign data
        data = b"This is test data"
        signature = crypto.sign_data(data)

        # Verify signature
        assert crypto.verify_signature(data, signature)

        # Verify with wrong data
        wrong_data = b"This is wrong data"
        assert not crypto.verify_signature(wrong_data, signature)

    def test_hash_computation(self):
        """Test hash computation."""
        data = {"key": "value", "number": 42}

        # Compute hash
        hash1 = CryptoManager.compute_hash(data)
        hash2 = CryptoManager.compute_hash(data)

        # Same data should produce same hash
        assert hash1 == hash2

        # Different data should produce different hash
        different_data = {"key": "different_value", "number": 42}
        hash3 = CryptoManager.compute_hash(different_data)
        assert hash3 != hash1

    def test_chain_hash_computation(self):
        """Test chain hash computation."""
        current_data = {"event": "test", "value": 123}
        previous_hash = "abc123"

        # Compute chain hash
        chain_hash = CryptoManager.compute_chain_hash(current_data, previous_hash)

        # Verify it includes previous hash
        data_with_prev = {**current_data, "previous_hash": previous_hash}
        expected_hash = CryptoManager.compute_hash(data_with_prev)
        assert chain_hash == expected_hash

    def test_timestamp_proof(self):
        """Test timestamp proof generation."""
        timestamp = datetime.now(pytz.UTC)

        # Generate proof
        proof1 = CryptoManager.generate_timestamp_proof(timestamp)
        proof2 = CryptoManager.generate_timestamp_proof(timestamp)

        # Same timestamp should produce same proof
        assert proof1 == proof2

        # Different timestamp should produce different proof
        different_time = timestamp + timedelta(seconds=1)
        proof3 = CryptoManager.generate_timestamp_proof(different_time)
        assert proof3 != proof1

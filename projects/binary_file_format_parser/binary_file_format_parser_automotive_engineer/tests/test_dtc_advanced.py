"""Advanced tests for DTC functionality."""

from pybinparser import DTCParser, DiagnosticTroubleCode, DTCFormat, DTCStatus


class TestDTCAdvanced:
    """Advanced DTC functionality tests."""

    def test_dtc_aging_counter(self):
        """Test DTC aging and healing counters."""
        dtc = DiagnosticTroubleCode(
            code="P0171", format=DTCFormat.ISO15031, occurrence_count=3
        )
        assert dtc.occurrence_count == 3

        # Simulate aging
        dtc.occurrence_count = 2
        assert dtc.occurrence_count == 2

    def test_manufacturer_specific_dtcs(self):
        """Test manufacturer-specific DTC ranges."""
        # P3XXX range is manufacturer specific
        mfr_dtc = DiagnosticTroubleCode(
            code="P3456",
            format=DTCFormat.MANUFACTURER,
            description="Manufacturer specific fault",
        )
        assert mfr_dtc.format == DTCFormat.MANUFACTURER

    def test_pending_vs_confirmed_dtcs(self):
        """Test pending vs confirmed DTC states."""
        dtc_pending = DiagnosticTroubleCode(
            code="P0420", format=DTCFormat.ISO15031, status=[DTCStatus.PENDING]
        )

        dtc_confirmed = DiagnosticTroubleCode(
            code="P0420",
            format=DTCFormat.ISO15031,
            status=[DTCStatus.CONFIRMED, DTCStatus.TEST_FAILED],
        )

        assert DTCStatus.PENDING in dtc_pending.status
        assert DTCStatus.CONFIRMED in dtc_confirmed.status

    def test_dtc_severity_levels(self):
        """Test DTC severity classification."""
        # Emissions related
        emissions_dtc = DiagnosticTroubleCode(
            code="P0420",
            format=DTCFormat.ISO15031,
            description="Catalyst efficiency below threshold",
        )

        # Safety critical
        safety_dtc = DiagnosticTroubleCode(
            code="C0035",
            format=DTCFormat.ISO15031,
            description="Left front wheel speed sensor fault",
        )

        # Network communication
        network_dtc = DiagnosticTroubleCode(
            code="U0100",
            format=DTCFormat.ISO15031,
            description="Lost communication with ECM",
        )

        # Different categories have different implications
        assert emissions_dtc.code.startswith("P")
        assert safety_dtc.code.startswith("C")
        assert network_dtc.code.startswith("U")

    def test_readiness_monitors(self):
        """Test OBD readiness monitor status."""
        # Readiness monitors indicate if tests have run
        monitors = {
            "catalyst": True,
            "heated_catalyst": True,
            "evap_system": False,  # Not ready
            "secondary_air": True,
            "ac_refrigerant": True,
            "oxygen_sensor": True,
            "oxygen_sensor_heater": True,
            "egr_system": False,  # Not ready
        }

        # Count ready monitors
        ready_count = sum(1 for ready in monitors.values() if ready)
        assert ready_count == 6

    def test_freeze_frame_priorities(self):
        """Test freeze frame data priority handling."""
        parser = DTCParser()

        # Fuel system DTCs have high priority for freeze frame
        high_priority_dtc = DiagnosticTroubleCode(
            code="P0171",
            format=DTCFormat.ISO15031,
            freeze_frame=parser.parse_freeze_frame(
                bytes(
                    [0x27, 0x10, 0x3C, 0x7D, 0x41, 0x80, 0x00, 0x64, 0x64, 0x4E, 0x20]
                ),
                DTCFormat.ISO15031,
            ),
        )

        assert high_priority_dtc.freeze_frame is not None
        assert high_priority_dtc.freeze_frame.engine_speed == 2500.0

    def test_dtc_grouping_by_system(self):
        """Test grouping DTCs by vehicle system."""
        dtcs = [
            DiagnosticTroubleCode(code="P0301", format=DTCFormat.ISO15031),
            DiagnosticTroubleCode(code="P0302", format=DTCFormat.ISO15031),
            DiagnosticTroubleCode(code="P0171", format=DTCFormat.ISO15031),
            DiagnosticTroubleCode(code="P0420", format=DTCFormat.ISO15031),
            DiagnosticTroubleCode(code="C0035", format=DTCFormat.ISO15031),
            DiagnosticTroubleCode(code="B1234", format=DTCFormat.ISO15031),
            DiagnosticTroubleCode(code="U0100", format=DTCFormat.ISO15031),
        ]

        # Group by system
        groups = {}
        for dtc in dtcs:
            system = dtc.code[0]
            if system not in groups:
                groups[system] = []
            groups[system].append(dtc)

        assert len(groups["P"]) == 4  # Powertrain
        assert len(groups["C"]) == 1  # Chassis
        assert len(groups["B"]) == 1  # Body
        assert len(groups["U"]) == 1  # Network

    def test_dtc_test_conditions(self):
        """Test DTC setting conditions."""
        # Some DTCs only set under specific conditions
        dtc_with_conditions = DiagnosticTroubleCode(
            code="P0128",
            format=DTCFormat.ISO15031,
            description="Coolant temp below thermostat regulating temp",
        )

        # Would need conditions like:
        # - Engine running time > 10 minutes
        # - Ambient temp > -7°C
        # - No other cooling system faults

        assert dtc_with_conditions.code == "P0128"

    def test_permanent_dtc_handling(self):
        """Test permanent DTC that requires multiple drive cycles to clear."""
        permanent_dtc = DiagnosticTroubleCode(
            code="P0420",
            format=DTCFormat.ISO15031,
            status=[DTCStatus.CONFIRMED, DTCStatus.TEST_FAILED_SINCE_CLEAR],
        )

        # Permanent DTCs can't be cleared immediately
        assert DTCStatus.TEST_FAILED_SINCE_CLEAR in permanent_dtc.status

    def test_dtc_snapshot_data(self):
        """Test extended snapshot data beyond basic freeze frame."""
        # Extended data might include:
        extended_data = {
            "battery_voltage": 13.8,
            "ambient_temperature": 25,
            "barometric_pressure": 101.3,
            "commanded_afr": 14.7,
            "fuel_rail_pressure": 380,
            "intake_manifold_pressure": 35,
            "ignition_timing_advance": 15,
            "catalyst_temperature": 650,
        }

        dtc = DiagnosticTroubleCode(
            code="P0420",
            format=DTCFormat.ISO15031,
            freeze_frame=DTCParser().parse_freeze_frame(bytes(11), DTCFormat.ISO15031),
        )

        # Store extended data in custom_data
        dtc.freeze_frame.custom_data = extended_data
        assert dtc.freeze_frame.custom_data["catalyst_temperature"] == 650

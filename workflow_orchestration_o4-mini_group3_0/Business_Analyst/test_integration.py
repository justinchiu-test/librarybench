import time
import pytest
from Business_Analyst.automation.interface import Interface
from Business_Analyst.automation.tasks import data_extraction, data_processing, report_generation

def test_full_workflow_integration():
    ui = Interface()
    # Setup user and login
    ui.add_user("analyst", roles=["user", "reporter"])
    ui.login("analyst")
    # Add tasks
    ui.add_task(name="data_extraction", func=data_extraction, priority=1)
    ui.add_task(
        name="data_processing",
        func=data_processing,
        priority=2,
        condition=lambda ctx: "data_extraction" in ctx
    )
    ui.add_task(
        name="report_generation",
        func=report_generation,
        priority=3,
        condition=lambda ctx: "data_processing" in ctx,
        required_role="reporter"
    )
    # Run workflow
    ui.run_pending()
    ctx = ui.get_context()
    # Check context contents
    assert "data_extraction" in ctx
    assert "data_processing" in ctx
    assert "report_generation" in ctx
    # Check that the report contains expected text
    report = ctx["report_generation"]
    assert "Report generated" in report
    # Notifications and logs recorded
    notifs = ui.get_notifications()
    assert any("data_extraction succeeded" in m for m in notifs)
    logs = ui.get_logs()
    assert any("Task added: data_extraction" in e for (_, e) in logs)

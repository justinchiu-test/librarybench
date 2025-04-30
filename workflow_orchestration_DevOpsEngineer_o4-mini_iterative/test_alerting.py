from tasks.alerting import PrintAlertService, AlertService

def test_alert_service_interface():
    svc = PrintAlertService()
    svc.send_alert("hello")
    assert svc.alerts == ["hello"]

    # Ensure inheritance
    assert isinstance(svc, AlertService)

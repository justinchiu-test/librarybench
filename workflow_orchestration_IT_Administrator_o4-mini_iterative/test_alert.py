from it_manager.alert import AlertManager

def test_alerts():
    AlertManager.clear_alerts()
    AlertManager.send_email("admin@example.com", "Test", "Body")
    AlertManager.send_message("sms", "Alert!")
    alerts = AlertManager.get_alerts()
    assert len(alerts) == 2
    assert "EMAIL to=admin@example.com" in alerts[0]
    assert "MSG channel=sms" in alerts[1]

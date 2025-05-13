import requests
import time
from postscheduler.health_check import start_health_check, stop_health_check

def test_health_endpoints():
    port = 8081
    runner = start_health_check(port=port)
    # give server a moment
    time.sleep(0.1)
    r1 = requests.get(f"http://127.0.0.1:{port}/live")
    r2 = requests.get(f"http://127.0.0.1:{port}/ready")
    assert r1.status_code == 200
    assert r1.text == "alive"
    assert r2.status_code == 200
    assert r2.text == "ready"
    stop_health_check(runner)

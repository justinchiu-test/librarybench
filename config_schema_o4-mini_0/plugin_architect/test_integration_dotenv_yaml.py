import tempfile
import yaml
from config_manager.utils import load_dotenv, load_yaml

def test_integration_env_and_yaml(tmp_path):
    # create .env
    env = tmp_path / ".env"
    env.write_text("KEY=val\nNUM=5")
    # create yaml referring to env values
    cfg = {"env_key": "KEY", "env_num": "NUM"}
    y = tmp_path / "c.yaml"
    y.write_text(yaml.safe_dump(cfg))
    data = load_dotenv(str(env))
    ydata = load_yaml(str(y))
    assert data["KEY"] == "val"
    assert ydata["env_key"] == "KEY"

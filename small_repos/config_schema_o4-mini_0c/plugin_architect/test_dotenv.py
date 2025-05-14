import tempfile
from config_manager.utils import load_dotenv

def test_dotenv_basic(tmp_path):
    f = tmp_path / ".env"
    f.write_text("A=1\nB=2\n#C=3\nD= four")
    data = load_dotenv(str(f))
    assert data == {"A":"1","B":"2","D":"four"}

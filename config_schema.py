import json
from jsonschema import validate
from pathlib import Path
from typing import Any, Dict

SCHEMA_PATH = Path(__file__).parent / "config" / "config_schema.json"
class ConfigError(Exception): pass

def load_and_validate_config(path: str) -> Dict[str, Any]:
    schema = json.loads(SCHEMA_PATH.read_text())
    data = json.loads(Path(path).read_text())
    try:
        validate(instance=data, schema=schema)
    except Exception as e:
        raise ConfigError(f"Invalid config: {e}")
    return data
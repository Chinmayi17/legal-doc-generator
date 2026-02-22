from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import runpy

ROOT_APP_PATH = Path(__file__).resolve().parent.parent / "app.py"


def _load_root_app_module():
    spec = spec_from_file_location("root_app", ROOT_APP_PATH)
    module = module_from_spec(spec)
    if spec and spec.loader:
        spec.loader.exec_module(module)
    return module


root_app_module = _load_root_app_module()
app = root_app_module.app


if __name__ == "__main__":
    runpy.run_path(str(ROOT_APP_PATH), run_name="__main__")

from pathlib import Path
from typing import Final

BASE_DIR: Final[Path] = Path(__file__).parent.parent
TEMPLATES_FOLDER: Final[Path] = BASE_DIR / "templates"

if not TEMPLATES_FOLDER.exists():
    raise ValueError(f"{TEMPLATES_FOLDER=} does not exist on disk.")

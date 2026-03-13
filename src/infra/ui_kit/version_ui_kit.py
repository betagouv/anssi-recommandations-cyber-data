import json
from pathlib import Path


def version_ui_kit() -> str:
    racine_projet = Path(__file__).resolve().parent.parent.parent.parent
    print(f"Racine du projet : {racine_projet}")
    package_json = racine_projet / "ui" / "package.json"

    data = json.loads(package_json.read_text(encoding="utf-8"))
    deps = data.get("dependencies", {})
    version = deps.get("@lab-anssi/ui-kit").replace("~", "").replace("^", "")

    return str(version)

import os
from pathlib import Path
import shutil
import subprocess

from uvicorn.importer import import_from_string
import yaml

APP_NAME = "reportsvc.app.main:app"
UGLY_NAME = "report-client"
NICE_NAME = "report_client"

SPEC_PATH = Path(__file__).resolve().parent.parent / "openapi.yaml"
GENERATED_CLIENT_PATH = Path(__file__).resolve().parent / UGLY_NAME
CLIENT_DIR = Path(__file__).resolve().parent.parent.parent.parent / "client"
CLIENT_PATH = CLIENT_DIR / NICE_NAME


def main():
    os.environ['SECRET_KEY'] = 'dummy'
    os.environ['SERVICE_ID'] = '-1'
    os.chdir(Path(__file__).resolve().parent)

    app = import_from_string(APP_NAME)
    openapi = app.openapi()
    version = openapi.get("openapi", "unknown version")

    print(f"writing openapi spec v{version}")
    with open(SPEC_PATH, "w") as f:
        yaml.dump(openapi, f, sort_keys=False)

    if GENERATED_CLIENT_PATH.exists():
        shutil.rmtree(GENERATED_CLIENT_PATH)
    subprocess.run([
        "openapi-python-client",
        "generate",
        "--path",
        SPEC_PATH])
    print('moving', GENERATED_CLIENT_PATH, 'to', CLIENT_PATH)
    if CLIENT_PATH.exists():
        shutil.rmtree(CLIENT_PATH)
    shutil.move(GENERATED_CLIENT_PATH, CLIENT_PATH)


if __name__ == "__main__":
    main()

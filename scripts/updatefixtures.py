import json
import os
import platform
from pathlib import Path

if "Windows" == platform.system():
    DATA_DIR = "D:/datos/data_dragon/data/es_MX/"
else:
    DATA_DIR = "/datos/data_dragon/data/es_MX/"

PROJECT_DIR = Path(__file__).resolve().parent.parent

def update_champions():
    """Actualiza el fixture de los campeones."""
    # Load data_dragon .json
    filepath = DATA_DIR + "champion.json"
    rawdata = {}
    champ_fixture = []
    if os.path.isfile(filepath):
        with open(filepath, 'r', encoding="utf8") as f:
            rawdata = json.load(f)

    # Create fixture data
    if rawdata is not {}:
        i = 1
        champions = rawdata.get('data', {})
        for name in sorted(champions.keys()):
            aux = {
                    "model": "champions.Champion",
                    "pk": i,
                    "fields": {
                        "identifier": champions[name]['id'],
                        "key": champions[name]['key'],
                        "name": champions[name]['name'],
                    }
                  }
            champ_fixture.append(aux)
            i += 1

    # Save fixture
    fixturepath = str(PROJECT_DIR / "champions/fixtures/champions.json")
    with open(fixturepath, 'w') as f:
        json.dump(champ_fixture, f)

def main():
    """Realiza las actualizaciones de los fixtures."""
    update_champions()

if __name__ == "__main__":
    main()

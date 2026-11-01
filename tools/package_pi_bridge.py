"""Build a source-only HA local app directory; never include private state."""
import argparse
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]


def build(destination):
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=False)
    for name in ('Dockerfile', 'config.yaml'):
        shutil.copyfile(ROOT / 'deployment/home-assistant' / name, destination / name)
    shutil.copyfile(ROOT / 'tools/requirements-m2.txt', destination / 'requirements-m2.txt')
    (destination / 'tools').mkdir()
    for source in (ROOT / 'tools').glob('*.py'):
        shutil.copyfile(source, destination / 'tools' / source.name)
    return destination


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('destination', type=Path)
    build(parser.parse_args().destination)

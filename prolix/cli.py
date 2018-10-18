
import os
import sys

from flask import cli as flask_cli


def main(as_module=False):
    # Cheat
    os.environ['FLASK_APP'] = "prolix.server.prolix_server.py"
    sys.argv = ['flask', 'run']
    flask_cli.main()

if __name__ == "__main__":
    main(as_module=True)



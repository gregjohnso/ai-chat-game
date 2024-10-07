# reads .secrets.json and sets each variable as an environment variable

import json
import logging
import os

logger = logging.getLogger(__name__)


# directory of this file
_my_dir = os.path.dirname(os.path.realpath(__file__))
# path of .secrets.json
_secrets_path = os.path.join(_my_dir, "../.secrets.json")


def load_secrets(overwrite_env=False):
    if os.path.isfile(_secrets_path):
        logger.info(f"Loading secrets from {_secrets_path}")
        with open(_secrets_path) as f:
            secrets = json.load(f)
            for key, value in secrets.items():
                if overwrite_env or key not in os.environ:
                    logger.info(f"Setting environment variable {key}")
                    os.environ[key] = value

    else:
        logger.warning(f"Secrets file not found at {_secrets_path}")

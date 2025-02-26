#!/usr/bin/env python

import config
import json
from follett_client import DestinyClient

fc = DestinyClient(config)

if __name__ == "__main__":
    print(json.dumps(fc.get_items()))
import os
import json

# load rule file
RULE_FILE = os.path.join(os.path.dirname(__file__), "rules.json")
with open(RULE_FILE, "r") as f:
    data = json.load(f)

# process and save rule file data
DL = [tuple(item) for item in data["bonusSquares"]["doubleLetter"]]
TL = [tuple(item) for item in data["bonusSquares"]["tripleLetter"]]
DW = [tuple(item) for item in data["bonusSquares"]["doubleWord"]]
TW = [tuple(item) for item in data["bonusSquares"]["tripleWord"]]

TILE_VALUE = data["tileValue"]
TILE_COUNT = data["tileCount"]
TILE_POOL = []
for tile, count in TILE_COUNT.items():
    TILE_POOL.extend([tile] * count)

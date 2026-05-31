import json
from braille_dict import BRAILLE_DICT

with open("braille_output.json") as f:
    data = json.load(f)

patterns = data["cells"]

known = 0

for p in patterns:
    if p in BRAILLE_DICT:
        known += 1

print("Known:", known)
print("Total:", len(patterns))
print("Coverage:", known / len(patterns) * 100, "%")
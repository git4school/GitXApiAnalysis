from tincan import *
from gittoxapi.differential import Differential, DiffPart
import json


def generate_sub_diffpart(
    parts: list[DiffPart], i: int, interval: tuple[int, int], modify_parent: bool
):
    part = parts[i]
    assert interval[0] > 0 and interval[1] < len(part.content)

    extracted = part.content[interval[0] : interval[1]]
    before_content = [l for l in extracted if l[0] != "+"]
    after_content = [l for l in extracted if l[0] != "-"]
    assert len(before_content) != len(after_content)

    newpart = DiffPart()
    newpart.a_start_line = part.a_start_line + interval[0]
    newpart.a_interval = len(before_content)

    newpart.b_start_line = part.a_start_line + interval[0]
    newpart.b_interval = len(after_content)

    newpart.content = extracted

    if not modify_parent:
        return newpart

    part.content = (
        part.content[: interval[0]]
        + [" " + l[1:] for l in extracted if l[0] != "-"]
        + part.content[interval[1] :]
    )

    shift = newpart.b_interval - newpart.a_interval

    part.a_interval += newpart.b_interval
    part.a_interval -= len(extracted) - len(after_content)

    for j in range(i + 1, len(parts)):
        part = parts[j]
        part.a_start_line += shift
        part.b_start_line += shift
    return newpart


raw = None
with open("original.json") as f:
    raw = json.load(f)
print(len(raw))

statements = [Statement(e) for e in raw]

for e in statements:
    e.object.definition.extensions["git"] = [
        Differential(v) for v in e.object.definition.extensions["git"]
    ]

find_statement = [
    e for e in statements if e.object.id == "ab6e7672319a429fa7213d100079433bc7054d8e"
][0]

diff: Differential = find_statement.object.definition.extensions["git"][0]
parts = diff.parts

newpart = generate_sub_diffpart(parts, 0, [3, 4], True)

print(json.dumps(newpart.__dict__, indent=2))

print(json.dumps([p.__dict__ for p in parts], indent=2))

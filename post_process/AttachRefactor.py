from tincan import *
from gittoxapi.differential import Differential, DiffPart
import json
import post_process.PostProcessModifier


class AttachRefactor(post_process.PostProcessModifier.PostProcessModifier):
    def __init__(self) -> None:
        with open("refactoring.json") as f:
            self.json = dict(
                [
                    (c["sha1"], c["refactorings"])
                    for c in json.load(f)["commits"]
                    if len(c["refactorings"]) > 0
                ]
            )

    def level(self):
        return Statement

    def _process(self, st_getter: any, i: int) -> list[tuple[Statement, bool]]:
        statement: Statement = st_getter(i)

        hash = statement.object.id

        if not hash in self.json:
            return

        if statement.context == None:
            statement.context = Context()

        if statement.context.extensions == None:
            statement.context.extensions = Extensions()

        statement.context.extensions["refactoring"] = self.json[hash]

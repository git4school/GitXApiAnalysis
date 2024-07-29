from typing import Callable
from tincan import Statement
from GitToXApi.differential import DiffPart, Differential
from modifier.code_modifier import *


class RemoveEmptyCodePartModifier(CodeModifier):

    def process_differential(
        self, st_getter: Callable[[int], Statement | None], i: int, diff: Differential
    ) -> list[Statement]:
        if diff.parts != None:
            diff.parts = [
                p
                for p in diff.parts
                if (p.content == None or any(l[0] in ["+", "-"] for l in p.content))
            ]

        return []

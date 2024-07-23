from typing import Callable
from tincan import Statement, Verb
from modifier.StatementModifier import StatementModifier
from gittoxapi.differential import Differential, DiffPart


class RemoveEmptyDifferentialModifier(StatementModifier):

    def process_statement(self, st_getter: Callable[[int], Statement | None], i: int):
        statement = st_getter(i)

        differentials: list[Differential] = statement.object.definition.extensions[
            "git"
        ]

        statement.object.definition.extensions["git"] = [
            d for d in differentials if d.parts != None and len(d.parts) > 0
        ]

        return [statement]

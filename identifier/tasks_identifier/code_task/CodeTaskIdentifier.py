from copy import deepcopy
from typing import Callable
from tincan import Statement
from gittoxapi.differential import DiffPart, Differential
from identifier.tasks_identifier.TaskIdentifier import TaskIdentifier
from modifier.code_modifier.CodeModifier import CodeModifier


class CodeTaskIdentifier(TaskIdentifier, CodeModifier):
    def __init__(self) -> None:
        super().__init__()

    def identifier_generator(
        self,
        statement: Statement,
        diff: Differential,
        i: int,
        intervals: list[tuple[int, int]],
        modifer: Callable[[Statement], None],
    ) -> Statement:
        return super().modifier_generator(statement, diff, i, intervals, modifer)

    def process_statement(
        self, st_getter: Callable[[int], Statement | None], i: int
    ) -> list[Statement]:

        statement: Statement = st_getter(i)
        if TaskIdentifier.is_task_set(statement):
            return [statement]
        return super().process_statement(st_getter, i)

from tincan import Statement, Context, ActivityDefinition, Extensions
from GitToXApi.differential import Differential, DiffPart
from typing import Callable
from identifier.ActivityIdentifier import ActivityIdentifier
from copy import deepcopy
from modifier.StatementModifier import StatementModifier


class TaskIdentifier(ActivityIdentifier, StatementModifier):
    def __init__(self) -> None:
        super().__init__()

    def get_task(statement: Statement) -> tuple[str, dict]:
        if not "task" in statement.context.extensions:
            return None
        task = statement.context.extensions["task"]
        id = task["id"]
        meta = task["metadata"]
        return (id, meta)

    def set_task(statement: Statement, id: str, metadata: dict):
        statement.context.extensions["task"] = {"id": id, "metadata": metadata}

    def task_applier(id: str, metadata: dict):
        return lambda statement: TaskIdentifier.set_task(statement, id, metadata)

    def is_task_set(statement: Statement):
        return TaskIdentifier.get_task(statement) != None

    def identifier_generator(
        self,
        statement: Statement,
        diff: Differential,
        modifer: Callable[[Statement], None],
    ) -> Statement:
        return self.modifier_generator(statement, diff, modifer)

    def process_statement(
        self, st_getter: Callable[[int], Statement | None], i: int
    ) -> list[Statement]:
        statement: Statement = st_getter(i)
        if TaskIdentifier.is_task_set(statement):
            return [statement]
        return super().process_statement(st_getter, i)

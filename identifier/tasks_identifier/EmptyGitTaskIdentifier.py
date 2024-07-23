from typing import Callable
from tincan import Statement
from gittoxapi.differential import Differential
from identifier.tasks_identifier.TaskIdentifier import TaskIdentifier


class EmptyGitTaskIdentifier(TaskIdentifier):

    def process_statement(
        self, st_getter: Callable[[int], Statement | None], i: int
    ) -> list[Statement]:

        statement = st_getter(i)
        if TaskIdentifier.is_task_set(statement):
            return [statement]

        if not "git" in statement.object.definition.extensions:
            return [statement]

        differentials: list[Differential] = statement.object.definition.extensions[
            "git"
        ]
        if len(differentials) == 0:
            TaskIdentifier.set_task(statement, "EmptyCommit", {})

        return [statement]

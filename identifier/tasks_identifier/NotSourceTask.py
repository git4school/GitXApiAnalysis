from typing import Callable
from tincan import Statement
from gittoxapi.differential import Differential
from identifier.tasks_identifier.TaskIdentifier import TaskIdentifier


class NotSourceTask(TaskIdentifier):

    def generator_prefix(self) -> str:
        return "notsource"

    def process_differential(
        self, st_getter: Callable[[int], Statement | None], i: int, diff: Differential
    ) -> Callable[[Statement], None]:
        if diff.file.endswith(".java"):
            return
        return TaskIdentifier.task_applier("NotSource", {})

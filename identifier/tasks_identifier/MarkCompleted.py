from typing import Callable
from tincan import Statement
from GitToXApi.differential import Differential
from identifier.tasks_identifier.TaskIdentifier import TaskIdentifier


class MarkCompleted(TaskIdentifier):

    def generator_prefix(self) -> str:
        return "resolved"

    def process_statement(
        self, st_getter: Callable[[int], Statement | None], i: int
    ) -> list[Statement]:

        statement = st_getter(i)

        if not statement.verb.id == "resolved":
            return [statement]

        statement.object.id = "http://curatr3.com/define/verb/edited"
        raw: str = statement.object.definition.description["en-US"]
        lines = raw.splitlines()
        data = {}
        lines[0] = lines[0][len("ITER_")]
        data = {"question": int(lines[0].strip())}
        if len(lines) > 1:
            data["difficulty"] = int(lines[1][len("D=")])
            data["emotion"] = int(lines[1][len("E=")])

        newstatement = self.modifier_generator(statement, None, lambda st: st)
        TaskIdentifier.set_task(newstatement, "Completed", data)

        return [statement, newstatement]

from typing import Callable
from tincan import Statement
from gittoxapi.differential import DiffPart, Differential
from identifier.tasks_identifier.code_task.CodeTaskIdentifier import *


class ImportTask(CodeTaskIdentifier):

    def generator_prefix(self) -> str:
        return "import"

    def process_part(
        self,
        st_getter: Callable[[int], Statement | None],
        i: int,
        diff: Differential,
        part: DiffPart,
    ) -> list[tuple[list[tuple[int, int]], Callable[[Statement], None]]]:
        extractions: list[tuple[int, str]] = []
        for i in range(len(part.content)):
            line = part.content[i]
            if line[0] != " " and line[1:].strip().startswith("import"):
                extractions.append(
                    (
                        i,
                        line[0] + (line[1:].strip()[len("import") :].strip()[:-1]),
                    )  # Extract import name and line symbol (+, -)
                )
        return [
            (
                [(v[0], v[0] + 1)],
                (
                    TaskIdentifier.task_applier(
                        "ImportStatement" + ("Add" if v[1][0] == "+" else "Remove"),
                        {"import": v[1:]},
                    )
                ),
            )
            for v in extractions
        ]

    def process_statement(
        self, st_getter: Callable[[int], Statement | None], i: int
    ) -> list[Statement]:
        statement = st_getter(i)
        if "editions" in statement.context.extensions:
            return [statement]
        return super().process_statement(st_getter, i)

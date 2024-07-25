from typing import Callable
from tincan import Statement
from gittoxapi.differential import DiffPart, Differential
from identifier.tasks_identifier.code_task.CodeTaskIdentifier import *


class SyntaxTypo(CodeTaskIdentifier):

    def generator_prefix(self) -> str:
        return "typo"

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
            if not line[0] in ["+", "-"]:
                continue

            if not line[1:].strip() in "{}()[];":
                continue

            extractions.append(
                (
                    i,
                    line[0] + (line[1:].strip()),
                )
            )
        return [
            (
                [(v[0], v[0] + 1)],
                (
                    TaskIdentifier.task_applier(
                        "SyntaxTypo" + ("Add" if v[1][0] == "+" else "Remove"),
                        {"content": v[1:]},
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
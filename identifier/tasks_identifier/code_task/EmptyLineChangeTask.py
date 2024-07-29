from typing import Callable
from tincan import Statement
from GitToXApi.differential import DiffPart, Differential
from identifier.tasks_identifier.code_task.CodeTaskIdentifier import *
import regex


class EmptyLineChangeTask(CodeTaskIdentifier):

    def generator_prefix(self) -> str:
        return "empty_line"

    def process_part(
        self,
        st_getter: Callable[[int], Statement | None],
        i: int,
        diff: Differential,
        part: DiffPart,
    ) -> list[tuple[list[tuple[int, int]], Callable[[Statement], None]]]:
        extractions: list[tuple[int, int]] = []

        i = 0
        while i < len(part.content):
            line = part.content[i]
            if not line[0] in ["+", "-"]:
                i += 1
                continue
            line: str = line[1:].strip().replace("\t", " ")
            if len(line.strip()) == 0:
                extractions.append((i, i + 1))
            i += 1

        return [
            (
                extractions,
                (
                    TaskIdentifier.task_applier(
                        "EmptyLine",
                        {},
                    )
                ),
            ),
        ]

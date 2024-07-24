from typing import Callable
from tincan import Statement
from gittoxapi.differential import DiffPart, Differential
from identifier.tasks_identifier.code_task.CodeTaskIdentifier import *
import regex
import utils


class BlockTask(CodeTaskIdentifier):

    def generator_prefix(self) -> str:
        return "block"

    def process_part(
        self,
        st_getter: Callable[[int], Statement | None],
        i: int,
        diff: Differential,
        part: DiffPart,
    ) -> list[tuple[list[tuple[int, int]], Callable[[Statement], None]]]:
        extractions: list[tuple[list[tuple[int, int]], bool]] = []

        i = 0
        while i < len(part.content):
            line = part.content[i]
            if not line[0] in ["+", "-"]:
                i += 1
                continue
            line: str = line[1:].strip().replace("\t", " ")

            if not line.startswith("{"):
                i += 1
                continue
            brackets_position = utils.find_delim(part.content, None, i, delim="{")
            if brackets_position == None:
                i += 1
                continue

            end_pos = brackets_position[1][0]
            end_line: str = part.content[end_pos]
            if end_line[0] != part.content[i][0] or not end_line[1:].strip().startswith(
                "}"
            ):
                i += 1
                continue

            extractions.append(
                (
                    [
                        (i, i + 1),
                        (brackets_position[1][0], brackets_position[1][0] + 1),
                    ],
                    line[0],
                )
            )

            i += 1
        return [
            (
                v[0],
                (
                    TaskIdentifier.task_applier(
                        "Block" + ("Add" if v[1] == "+" else "Remove"),
                        {},
                    )
                ),
            )
            for v in extractions
        ]

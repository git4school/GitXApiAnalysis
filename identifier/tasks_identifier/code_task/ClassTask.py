from typing import Callable
from tincan import Statement
from GitToXApi.differential import DiffPart, Differential
from identifier.tasks_identifier.code_task.CodeTaskIdentifier import *
import regex
import utils


class ClassTask(CodeTaskIdentifier):

    def generator_prefix(self) -> str:
        return "class_addition"

    def process_part(
        self,
        st_getter: Callable[[int], Statement | None],
        i: int,
        diff: Differential,
        part: DiffPart,
    ) -> list[tuple[list[tuple[int, int]], Callable[[Statement], None]]]:
        extractions: list[tuple[list[tuple[int, int]], str, str]] = []

        i = 0
        while i < len(part.content):
            line = part.content[i]
            symbol = line[0]
            if not symbol in ["+", "-"]:
                i += 1
                continue
            line: str = line[1:].strip().replace("\t", " ")

            if regex.match("(|public) *class", line):
                name = line[(line.index("class") + len("class")) :].strip()
                name = name[: (name + " ").index(" ")]
                name = name[: (name + "{").index("{")]
                name = name.strip()
                brackets_position = utils.find_delim(part.content, None, i, delim="{")

                if (
                    brackets_position != None
                    and part.content[brackets_position[0][0]][0] == symbol
                    and part.content[brackets_position[1][0]][0] == symbol
                ):
                    extractions.append(
                        (
                            [
                                (i, brackets_position[0][0] + 1),
                                (brackets_position[1][0], brackets_position[1][0] + 1),
                            ],
                            symbol,
                            name,
                        )
                    )
            i += 1
        return [
            (
                v[0],
                (
                    TaskIdentifier.task_applier(
                        "Class" + ("Add" if v[1] == "+" else "Remove"),
                        {"name": v[1]},
                    )
                ),
            )
            for v in extractions
        ]

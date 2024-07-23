from typing import Callable
from tincan import Statement
from gittoxapi.differential import DiffPart, Differential
from identifier.tasks_identifier.code_task.CodeTaskIdentifier import *
import regex
import utils


class IfAdditionTask(CodeTaskIdentifier):

    def generator_prefix(self) -> str:
        return "if_addition"

    def process_part(
        self,
        st_getter: Callable[[int], Statement | None],
        i: int,
        diff: Differential,
        part: DiffPart,
    ) -> list[tuple[list[tuple[int, int]], Callable[[Statement], None]]]:
        extractions: list[tuple[list[tuple[int, int]], str]] = []

        i = 0
        while i < len(part.content):
            line = part.content[i]
            if line[0] != "+":
                i += 1
                continue
            line: str = line[1:].strip().replace("\t", " ")
            if (
                line.startswith("if")
                or line.replace(" ", "").startswith("elseif")
                or line.replace(" ", "").startswith("}elseif")
            ):
                line = line[line.index("if") + len("if") :]
                parantheses_position = utils.find_delim(
                    part.content, None, i, delim="("
                )
                if parantheses_position == None:
                    i += 1
                    continue
                brackets_position = utils.find_delim(
                    part.content, None, parantheses_position[1][0], delim="{"
                )
                if brackets_position == None or any(
                    ";" in l
                    for l in part.content[
                        parantheses_position[1][0] : brackets_position[0][0] - 1
                    ]
                ):
                    extractions.append(
                        (
                            [(i, parantheses_position[1][0] + 1)],
                            line,
                        )
                    )
                else:
                    extractions.append(
                        (
                            [
                                (i, brackets_position[0][0] + 1),
                                (brackets_position[1][0], brackets_position[1][0] + 1),
                            ],
                            line,
                        )
                    )

                    i = brackets_position[1][0]
                    continue
            elif line.startswith("else") or line.replace(" ", "").startswith("}else"):
                brackets_position = utils.find_delim(part.content, None, i, delim="{")
                extractions.append(
                    (
                        [
                            (i, brackets_position[0][0] + 1),
                            (brackets_position[1][0], brackets_position[1][0] + 1),
                        ],
                        line,
                    )
                )

                i = brackets_position[1][0]
                continue
            i += 1
        return [
            (
                v[0],
                (
                    TaskIdentifier.task_applier(
                        "IfAddition",
                        {"content": v[1]},
                    )
                ),
            )
            for v in extractions
        ]

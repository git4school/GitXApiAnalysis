from typing import Callable
from tincan import Statement
from GitToXApi.differential import DiffPart, Differential
from identifier.tasks_identifier.code_task.CodeTaskIdentifier import *
import regex
import utils


class IfTask(CodeTaskIdentifier):

    def generator_prefix(self) -> str:
        return "if_addition"

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
                if (
                    brackets_position == None
                    or any(
                        ";" in l
                        for l in part.content[
                            parantheses_position[1][0] : brackets_position[0][0] - 1
                        ]
                    )
                    or part.content[brackets_position[0][0]][0] != symbol
                    or part.content[brackets_position[1][0]][0] != symbol
                ):
                    extractions.append(
                        (
                            [(i, parantheses_position[1][0] + 1)],
                            symbol,
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
                            symbol,
                            line,
                        )
                    )
            elif line.startswith("else") or line.replace(" ", "").startswith("}else"):
                line = line[line.index("else") + len("else") :]
                brackets_position = utils.find_delim(part.content, None, i, delim="{")
                if (
                    brackets_position == None
                    or part.content[brackets_position[0][0]][0] != symbol
                    or part.content[brackets_position[1][0]][0] != symbol
                ):
                    extractions.append(
                        (
                            [(i, i + 1)],
                            symbol,
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
                            symbol,
                            line,
                        )
                    )
            i += 1
        return [
            (
                v[0],
                (
                    TaskIdentifier.task_applier(
                        "If" + ("Add" if v[1] == "+" else "Remove"),
                        {"content": v[2]},
                    )
                ),
            )
            for v in extractions
        ]

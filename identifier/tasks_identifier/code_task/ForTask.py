from typing import Callable
from tincan import Statement
from gittoxapi.differential import DiffPart, Differential
from identifier.tasks_identifier.code_task.CodeTaskIdentifier import *
import regex
import utils


class ForTask(CodeTaskIdentifier):

    def generator_prefix(self) -> str:
        return "for_addition"

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
            if line.startswith("for"):
                line = line[line.index("for") + len("for") :]
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
                    or part.content[brackets_position[0][0]][0] != symbol
                    or part.content[brackets_position[1][0]][0] != symbol
                ):
                    i += 1
                    continue
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
                        "For" + ("Add" if v[1] == "+" else "Remove"),
                        {"content": v[2]},
                    )
                ),
            )
            for v in extractions
        ]

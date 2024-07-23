from typing import Callable
from tincan import Statement
from gittoxapi.differential import DiffPart, Differential
from identifier.tasks_identifier.code_task.CodeTaskIdentifier import *
import regex
import utils


class ForAdditionTask(CodeTaskIdentifier):

    def generator_prefix(self) -> str:
        return "for_addition"

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
                if brackets_position == None:
                    i += 1
                    continue
                extractions.append(
                    (
                        [
                            (i, brackets_position[0][0] + 1),
                            (brackets_position[1][0], brackets_position[1][0] + 1),
                        ],
                        line,
                    )
                )
            i += 1
        return [
            (
                v[0],
                (
                    TaskIdentifier.task_applier(
                        "ForAddition",
                        {"content": v[1]},
                    )
                ),
            )
            for v in extractions
        ]

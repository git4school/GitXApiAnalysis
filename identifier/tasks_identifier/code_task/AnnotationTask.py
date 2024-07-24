from typing import Callable
from tincan import Statement
from gittoxapi.differential import DiffPart, Differential
from identifier.tasks_identifier.code_task.CodeTaskIdentifier import *
import regex
import utils


class AnnotationTask(CodeTaskIdentifier):

    def generator_prefix(self) -> str:
        return "annotation_addition"

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
            if line.startswith("@"):
                line = line[line.index("@") + 1 :]

                parantheses_position = utils.find_delim(
                    part.content, None, i, delim="("
                )

                if (
                    parantheses_position == None
                    or part.content[parantheses_position[0][0]][0] != symbol
                    or part.content[parantheses_position[1][0]][0] != symbol
                ):
                    extractions.append(([(i, i + 1)], symbol, line))
                    i = parantheses_position[1][0]
                else:
                    extractions.append(
                        (
                            [
                                (i, parantheses_position[0][0]),
                                (
                                    parantheses_position[1][0],
                                    parantheses_position[1][0] + 1,
                                ),
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
                        "Annotation" + ("Add" if v[1] == "+" else "Remove"),
                        {"content": v[2]},
                    )
                ),
            )
            for v in extractions
        ]

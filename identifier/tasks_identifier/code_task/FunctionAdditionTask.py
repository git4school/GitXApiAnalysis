from typing import Callable
from tincan import Statement
from gittoxapi.differential import DiffPart, Differential
from identifier.tasks_identifier.code_task.CodeTaskIdentifier import *
import regex
import utils


class FunctionAdditionTask(CodeTaskIdentifier):

    def generator_prefix(self) -> str:
        return "function_addition"

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
                regex.match(
                    "(public |protected |private |static )*[\w\<\>\[\]]+\s+(\w+) *\([^\)]*\) *(\{?|[^;])",
                    line,
                )
                != None
            ):
                if "{" in line:
                    line = line[: line.index("{")].strip()

                initial_i = i
                first = -1
                last = -1
                opened = 0
                brackets = utils.find_delim(part.content, None, i, delim="{")

                if brackets != None:
                    extractions.append(
                        (
                            [
                                (i, brackets[0][0] + 1),
                                (brackets[1][0], brackets[1][0] + 1),
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
                        "FunctionAddition",
                        {"content": v[1]},
                    )
                ),
            )
            for v in extractions
        ]

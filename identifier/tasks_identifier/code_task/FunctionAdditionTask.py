from typing import Callable
from tincan import Statement
from gittoxapi.differential import DiffPart, Differential
from identifier.tasks_identifier.code_task.CodeTaskIdentifier import *
import regex


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
                while last == -1 and i < len(part.content):
                    current_line: str = part.content[i]
                    if (
                        first == -1
                        and current_line.count("{") - current_line.count("}") > 0
                    ):
                        first = i
                        opened = current_line.count("{") - current_line.count("}")
                    else:
                        opened += current_line.count("{") - current_line.count("}")

                    if first != -1 and last == -1 and opened <= 0:
                        last = i
                    i += 1
                if last != -1:
                    first_1 = min(initial_i, first)
                    first_2 = max(initial_i + 1, first + 1)
                    extractions.append(([(first_1, first_2), (last, last + 1)], line))
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

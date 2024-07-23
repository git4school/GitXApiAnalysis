from typing import Callable
from tincan import Statement
from gittoxapi.differential import DiffPart, Differential
from identifier.tasks_identifier.code_task.CodeTaskIdentifier import *
import regex


class ClassAdditionTask(CodeTaskIdentifier):

    def generator_prefix(self) -> str:
        return "class_addition"

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

            if regex.match("(|public) *class", line):
                name = line[(line.index("class") + len("class")) :].strip()
                name = name[: (name + " ").index(" ")]
                name = name[: (name + "{").index("{")]
                name = name.strip()
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
                    extractions.append(([(first, first + 1), (last, last + 1)], name))
            i += 1
        return [
            (
                v[0],
                (
                    TaskIdentifier.task_applier(
                        "ClassAddition",
                        {"name": v[1]},
                    )
                ),
            )
            for v in extractions
        ]

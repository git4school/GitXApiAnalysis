from typing import Callable
from tincan import Statement
from GitToXApi.differential import DiffPart, Differential
from identifier.tasks_identifier.code_task.CodeTaskIdentifier import *


class LineBreakAndSpacingChangeTask(CodeTaskIdentifier):

    def generator_prefix(self) -> str:
        return "linebreak"

    def process_part(
        self,
        st_getter: Callable[[int], Statement | None],
        i: int,
        diff: Differential,
        part: DiffPart,
    ) -> list[tuple[list[tuple[int, int]], Callable[[Statement], None]]]:
        extractions: list[int] = []
        buffer_del = ""
        buffer_add = ""
        begin_i = -1
        for line_i in range(len(part.content)):
            line: str = part.content[line_i]
            if len(line) == 0 or line.startswith(" "):
                buffer_del = ""
                buffer_add = ""
                begin_i = -1
            if line.startswith("-"):
                buffer_del = buffer_del + line[1:]
                if begin_i == -1:
                    begin_i = line_i
            if line.startswith("+"):
                buffer_add = buffer_add + line[1:]
                if (
                    buffer_add.replace(" ", "").replace("\t", "")
                    == buffer_del.replace(" ", "").replace("\t", "")
                    and len(buffer_del.strip()) != 0
                    and len(buffer_add.strip()) != 0
                ):
                    extractions.append((begin_i, line_i + 1))
                    buffer_add = ""
                    buffer_del = ""
                    begin_i = -1

        return [
            (
                [(v[0], v[1])],
                (
                    TaskIdentifier.task_applier(
                        "LineBreakChange" if (v[1] - v[0] > 2) else "LineSpacingChange",
                        {},
                    )
                ),
            )
            for v in extractions
        ]

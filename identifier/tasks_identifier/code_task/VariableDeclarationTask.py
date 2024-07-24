from typing import Callable
from tincan import Statement
from gittoxapi.differential import DiffPart, Differential
from identifier.tasks_identifier.code_task.CodeTaskIdentifier import *


class VariableDeclarationTask(CodeTaskIdentifier):

    def generator_prefix(self) -> str:
        return "variable_declaration"

    def process_part(
        self,
        st_getter: Callable[[int], Statement | None],
        i: int,
        diff: Differential,
        part: DiffPart,
    ) -> list[tuple[list[tuple[int, int]], Callable[[Statement], None]]]:
        extractions: list[tuple[int, str, str, dict]] = []
        for i in range(len(part.content)):
            line = part.content[i]
            if line[0] in ["+", "-"]:

                content: str = line[1:].strip().replace("\t", " ")

                if not "=" in content:
                    continue

                equal_i = content.index("=")
                if (
                    equal_i + 1 != len(content) and content[equal_i + 1] == "="
                ) or equal_i == 0:
                    continue
                if ("//" in content and content.index("//") < equal_i) or (
                    "/*" in content and content.index("/*") < equal_i
                ):
                    continue

                parts = content.split("=", maxsplit=2)
                if "(" in parts[0]:
                    continue

                extractions.append(
                    (
                        i,
                        line[0],
                        "Declaration" if " " in parts[0].strip() else "VariableAssign",
                        {"declaration": parts[0].strip(), "value": parts[1].strip()},
                    )
                )
        return [
            (
                [(v[0], v[0] + 1)],
                (
                    TaskIdentifier.task_applier(
                        v[2] + "Statement" + ("Add" if v[1][0] == "+" else "Remove"),
                        v[3],
                    )
                ),
            )
            for v in extractions
        ]

    def process_statement(
        self, st_getter: Callable[[int], Statement | None], i: int
    ) -> list[Statement]:
        statement = st_getter(i)
        if "editions" in statement.context.extensions:
            return [statement]
        return super().process_statement(st_getter, i)

from typing import Callable
from tincan import Statement
from gittoxapi.differential import DiffPart, Differential
from identifier.tasks_identifier.code_task.CodeTaskIdentifier import *
import json
import debug


class RefactoringMinerTask(CodeTaskIdentifier):

    def __init__(self) -> None:
        with open("refactoring.json") as f:
            self.json = dict(
                [
                    (c["sha1"], c["refactorings"])
                    for c in json.load(f)["commits"]
                    if len(c["refactorings"]) > 0
                ]
            )

    def generator_prefix(self) -> str:
        return "refactoring_miner"

    def process_part(
        self,
        st_getter: Callable[[int], Statement | None],
        i: int,
        diff: Differential,
        part: DiffPart,
    ) -> list[tuple[list[tuple[int, int]], Callable[[Statement], None]]]:
        extractions: list[tuple[list[tuple[int, int]], Callable[[Statement], None]]] = (
            []
        )
        statement = st_getter(i)
        hash = statement.object.id
        if "~" in hash or not hash in self.json or self.json[hash] == None:
            return
        refactorings = self.json[hash]
        refactorings = [r for r in refactorings if r != None]
        refact_i = 0
        while refact_i < len(refactorings):
            refact = refactorings[refact_i]
            refact_type = refact["type"]
            refact_i += 1

            if refact_type in ["Extract Method"]:
                if debug.DEBUG_MODE:
                    print(refact_type, "NOT MATCHED", "hash:(", hash, ")")
                continue

            before = (
                refact["leftSideLocations"][0]
                if len(refact["leftSideLocations"]) > 0
                else None
            )

            after = (
                refact["rightSideLocations"][0]
                if len(refact["rightSideLocations"]) > 0
                else None
            )

            beforeStartLine = before["startLine"]
            beforeEndLine = before["endLine"]
            afterStartLine = after["startLine"]
            afterEndLine = after["endLine"]

            if not (
                part.a_start_line < before["startLine"]
                and (
                    part.a_start_line + part.a_interval > before["endLine"]
                    or refact_type in ["Add Method Annotation"]
                )
            ):
                continue

            before_real_interval = [0, 1]
            before_matched_lines = 0

            after_real_interval = [0, 1]
            after_matched_lines = 0

            for i in range(len(part.content)):
                line = part.content[i]

                if not line.startswith("+"):
                    before_matched_lines += 1
                if before_matched_lines + part.a_start_line <= beforeStartLine:
                    before_real_interval[0] += 1
                    before_real_interval[1] += 1
                elif before_matched_lines + part.a_start_line <= beforeEndLine:
                    before_real_interval[1] += 1

                if not line.startswith("-"):
                    after_matched_lines += 1
                if after_matched_lines + part.b_start_line <= afterStartLine:
                    after_real_interval[0] += 1
                    after_real_interval[1] += 1
                elif after_matched_lines + part.b_start_line <= afterEndLine:
                    after_real_interval[1] += 1

            newpart = False

            if before["codeElementType"] == "METHOD_DECLARATION":
                while before_real_interval[0] < len(part.content) and part.content[
                    before_real_interval[0]
                ].strip().startswith("@"):
                    before_real_interval[0] += 1
                    while part.content[before_real_interval[0]].startswith("+"):
                        before_real_interval[0] += 1

            if after["codeElementType"] == "METHOD_DECLARATION":
                while after_real_interval[0] < len(part.content) and part.content[
                    after_real_interval[0]
                ].strip().startswith("@"):
                    after_real_interval[0] += 1
                    while part.content[after_real_interval[0]].startswith("-"):
                        after_real_interval[0] += 1

            if refact_type in "Add Parameter":
                newpart = True
                before_real_interval = [
                    before_real_interval[0],
                    before_real_interval[0] + 1,
                ]
            elif refact_type in [
                "Rename Method",
                "Rename Variable",
                "Rename Parameter",
                "Change Return Type",
                "Parameterize Variable",
                "Change Variable Type",
                "Change Attribute Type",
                "Change Parameter Type",
                "Invert Condition",
                "Localize Parameter",
                "Remove Parameter",
                "Add Parameter",
                "Add Method Annotation",
            ]:
                newpart = True
                before_real_interval = [
                    before_real_interval[0],
                    before_real_interval[0] + 1,
                ]
                after_real_interval = [
                    after_real_interval[0],
                    after_real_interval[0] + 1,
                ]

            if newpart:
                extractions.append(
                    (
                        [
                            before_real_interval,
                            after_real_interval,
                        ],
                        TaskIdentifier.task_applier("RefactoringMiner", refact),
                    )
                )

                refactorings[refact_i - 1] = None
                refactorings = [r for r in refactorings if r != None]
            if debug.DEBUG_MODE:
                print(refact_type, "NOT MATCHED", "hash:(", hash, ")")
        return [(l, c) for (l, c) in extractions]

    def process_statement(
        self, st_getter: Callable[[int], Statement | None], i: int
    ) -> list[Statement]:
        statement = st_getter(i)
        if "editions" in statement.context.extensions:
            return [statement]
        returns = super().process_statement(st_getter, i)
        if statement.object.id in self.json:
            self.json[statement.object.id] = None
        return returns

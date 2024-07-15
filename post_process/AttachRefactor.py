from tincan import *
from gittoxapi.differential import Differential, DiffPart
import json
import post_process.PostProcessModifier
import copy
import debug


class AttachRefactor(post_process.PostProcessModifier.PostProcessModifier):
    def __init__(self) -> None:
        with open("refactoring.json") as f:
            self.json = dict(
                [
                    (c["sha1"], c["refactorings"])
                    for c in json.load(f)["commits"]
                    if len(c["refactorings"]) > 0
                ]
            )

    def level(self):
        return Statement

    def _process(self, st_getter: any, i: int) -> list[tuple[Statement, bool]]:
        statement: Statement = st_getter(i)

        hash = statement.object.id

        if not hash in self.json:
            return

        if statement.context == None:
            statement.context = Context()

        if statement.context.extensions == None:
            statement.context.extensions = Extensions()

        if not "refactoring" in statement.context.extensions:
            statement.context.extensions["refactoring"] = self.json[hash]

        refactorings = statement.context.extensions["refactoring"]

        if refactorings == None:
            return

        refactorings = [r for r in refactorings if r != None]

        if len(refactorings) == 0:
            statement.context.extensions["refactoring"] = None
            return

        stmts = []

        refact_i = 0

        while refact_i < len(refactorings):
            refact = refactorings[refact_i]
            refact_type = refact["type"]

            refact_i += 1

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

            beforeFile = before["filePath"]
            beforeStartLine = before["startLine"]
            beforeEndLine = before["endLine"]
            afterFile = after["filePath"]
            afterStartLine = after["startLine"]
            afterEndLine = after["endLine"]

            diffpart_i = 0

            diffs: Differential = [
                o
                for o in statement.object.definition.extensions["git"]
                if o.file in [beforeFile, afterFile]
            ]

            for diff in diffs:
                for diffpart in diff.parts:

                    diffpart: DiffPart = diffpart
                    diffpart_i += 1

                    if not (
                        diffpart.a_start_line < before["startLine"]
                        and (
                            diffpart.a_start_line + diffpart.a_interval
                            > before["endLine"]
                            or refact_type in ["Add Method Annotation"]
                        )
                    ):
                        continue

                    before_real_interval = [0, 1]
                    before_matched_lines = 0

                    after_real_interval = [0, 1]
                    after_matched_lines = 0

                    for i in range(len(diffpart.content)):
                        line = diffpart.content[i]

                        if line[0] != "+":
                            before_matched_lines += 1
                        if (
                            before_matched_lines + diffpart.a_start_line
                            <= beforeStartLine
                        ):
                            before_real_interval[0] += 1
                            before_real_interval[1] += 1
                        elif (
                            before_matched_lines + diffpart.a_start_line
                            <= beforeEndLine
                        ):
                            before_real_interval[1] += 1

                        if line[0] != "-":
                            after_matched_lines += 1
                        if (
                            after_matched_lines + diffpart.b_start_line
                            <= afterStartLine
                        ):
                            after_real_interval[0] += 1
                            after_real_interval[1] += 1
                        elif (
                            after_matched_lines + diffpart.b_start_line <= afterEndLine
                        ):
                            after_real_interval[1] += 1

                    newpart = False

                    if before["codeElementType"] == "METHOD_DECLARATION":
                        while before_real_interval[0] < len(
                            diffpart.content
                        ) and diffpart.content[
                            before_real_interval[0]
                        ].strip().startswith(
                            "@"
                        ):
                            before_real_interval[0] += 1
                            while diffpart.content[before_real_interval[0]].startswith(
                                "+"
                            ):
                                before_real_interval[0] += 1

                    if after["codeElementType"] == "METHOD_DECLARATION":
                        while after_real_interval[0] < len(
                            diffpart.content
                        ) and diffpart.content[
                            after_real_interval[0]
                        ].strip().startswith(
                            "@"
                        ):
                            after_real_interval[0] += 1
                            while diffpart.content[after_real_interval[0]].startswith(
                                "-"
                            ):
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
                        newpart: DiffPart = (
                            post_process.PostProcessModifier.PostProcessModifier.generate_sub_diffpart(
                                diff.parts,
                                diffpart_i - 1,
                                [
                                    before_real_interval,
                                    after_real_interval,
                                ],
                                True,
                            )
                        )

                        newstatement: Statement = copy.deepcopy(statement)

                        commitOnlyRefactor = all(
                            len(l) == 0 or l[0] == " " for l in diffpart.content
                        )

                        if not commitOnlyRefactor:
                            newstatement.object.id = (
                                "generated~"
                                + newstatement.object.id
                                + "~"
                                + diff.file
                                + "~"
                                + str(newpart.a_start_line)
                            )
                        newdifferential: Differential = Differential(diff.__dict__)
                        newstatement.object.definition.extensions["git"] = [
                            newdifferential
                        ]
                        newstatement.context.extensions["atomic"] = True

                        newdifferential.parts = []
                        newdifferential.parts.append(newpart)

                        refactorings[refact_i - 1] = None
                        refactorings = [r for r in refactorings if r != None]
                        if len(refactorings) == 0:
                            refactorings = None
                        statement.context.extensions["refactoring"] = refactorings

                        if commitOnlyRefactor:
                            return [(newstatement, False)]
                        else:
                            return [(newstatement, False), (statement, True)]
            if debug.DEBUG_MODE:
                print(refact_type, "NOT MATCHED", "hash:(", hash, ")")

    def exec_refactoring(
        shift_before, before, before_content, shift_after, after, after_content
    ):
        """
        Return intermediate content with no refactoring and all code change

        Args:
            shift_before (_type_): _description_
            before (_type_): _description_
            before_content (_type_): _description_
            shift_after (_type_): _description_
            after (_type_): _description_
            after_content (_type_): _description_

        Returns:
            _type_: _description_
        """
        if before == None and after == None:
            return

        before_beginrow, before_begincol, before_endrow, before_endcol = (
            (
                before["startLine"] - shift_before,
                before["startColumn"] - 1,
                before["endLine"] - shift_before,
                before["endColumn"] - 1,
            )
            if before != None
            else (None, None, None, None)
        )

        after_beginrow, after_begincol, after_endrow, after_endcol = (
            (
                after["startLine"] - shift_after,
                after["startColumn"] - 1,
                after["endLine"] - shift_after,
                after["endColumn"] - 1,
            )
            if after != None
            else (None, None, None, None)
        )

        if after != None:
            # Manage trailing commas
            before_stripped = after_content[after_beginrow][:after_begincol].strip()
            if len(before_stripped) != 0 and before_stripped[-1] == ",":
                after_begincol = after_content[after_beginrow][:after_begincol].rfind(
                    ","
                )

            # Remove refactoring
            if after_beginrow == after_endrow:
                # If the interval is within a single line
                after_content[after_beginrow] = (
                    after_content[after_beginrow][:after_begincol]
                    + after_content[after_beginrow][after_endcol:]
                )
            else:
                # Remove text in the first line from begincol to the end of the line
                after_content[after_beginrow] = (
                    after_content[after_beginrow][:after_begincol] + "\n"
                )
                # Remove text in the last line from the start to endcol
                after_content[after_endrow] = after_content[after_endrow][after_endcol:]

                for i in range(after_beginrow + 1, after_endrow):
                    after_content[i] = ""

                # Remove all lines in between but keep one empty lines
                after_content = (
                    after_content[: after_beginrow + 1]
                    + after_content[after_endrow + 1 :]
                )

        if before != None and (
            not before["description"] == "original method declaration"
        ):

            raw = before_content[before_beginrow : before_endrow + 1]

            if len(raw) == 1:
                raw[0] = raw[0][before_begincol:before_endcol]
            else:
                raw[0] = raw[0][before_begincol:]
                raw[-1] = raw[-1][:before_endcol] + "\n"

            raw = "\n".join(raw)

            after_content[after_beginrow] = (
                after_content[after_beginrow][:after_begincol]
                + raw
                + after_content[after_beginrow][after_begincol:]
            )

        return after_content

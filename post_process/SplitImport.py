from post_process.PostProcessModifier import PostProcessModifier
from gittoxapi.differential import DiffPart, Differential
from tincan import Statement, Verb
from tincan import *
import copy


class SplitImport(PostProcessModifier):

    def _process(self, st_getter: any, i: int) -> list[tuple[Statement, bool]]:

        statement: Statement = st_getter(i)

        if not "git" in statement.object.definition.extensions:
            return

        if statement.context.extensions["atomic"]:
            return

        statements = [(statement, False)]
        differentials: list[Differential] = statement.object.definition.extensions[
            "git"
        ]

        diff_i = 0
        while diff_i < len(differentials):
            diff = differentials[diff_i]
            if diff.parts == None:
                diff_i += 1
                continue

            for part_i in range(len(diff.parts)):
                part = diff.parts[part_i]

                if part == None or part.content == None:
                    continue
                content = part.content

                last_import_line = 0
                while (last_import_line) < len(content) and (
                    len(content[last_import_line][1:].strip()) == 0
                    or content[last_import_line][0] == " "
                    or content[last_import_line][1:].startswith("import")
                ):
                    last_import_line += 1

                if last_import_line == 0 or all(
                    not (l[1:].startswith("import") and l[0] != " ")
                    for l in content[:last_import_line]
                ):
                    continue

                newpart: DiffPart = PostProcessModifier.generate_sub_diffpart(
                    diff.parts,
                    part_i,
                    [(0, last_import_line)],
                    True,
                )

                newstatement: Statement = copy.deepcopy(statement)

                newstatement.object.id = (
                    "generated~import~"
                    + newstatement.object.id
                    + "~"
                    + diff.file
                    + "~"
                    + str(newpart.a_start_line)
                )

                newdifferential: Differential = Differential(diff.__dict__)
                newstatement.object.definition.extensions["git"] = [newdifferential]
                newstatement.context.extensions["atomic"] = True

                newdifferential.parts = []
                newdifferential.parts.append(newpart)

                statement.context.extensions["refactoring"] = []
                statements.append((newstatement, False))
            else:
                diff_i += 1

        return statements

from post_process.PostProcessModifier import PostProcessModifier
from gittoxapi.differential import DiffPart, Differential
from tincan import Statement, Verb
from tincan import *
import copy


class LineFuser(PostProcessModifier):

    def level(self):
        return Statement

    def _process(self, st_getter: any, i: int) -> list[tuple[Statement, bool]]:

        statement: Statement = st_getter(i)

        if not "git" in statement.object.definition.extensions:
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
                            newpart: DiffPart = (
                                PostProcessModifier.generate_sub_diffpart(
                                    diff.parts,
                                    part_i,
                                    [(begin_i, line_i + 1)],
                                    True,
                                )
                            )

                            newstatement: Statement = copy.deepcopy(statement)

                            newstatement.object.id = (
                                "generated~linefuser~"
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
                            newstatement.context.extensions["classified"].append(
                                "REFACTORING"
                            )

                            newdifferential.parts = []
                            newdifferential.parts.append(newpart)

                            statement.context.extensions["refactoring"] = []
                            statements.append((newstatement, False))
                            break
                else:
                    continue
                break
            else:
                diff_i += 1

        return statements

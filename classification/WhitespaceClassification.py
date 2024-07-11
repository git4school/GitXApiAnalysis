from tincan import *
from gittoxapi.differential import Differential, DiffPart


import classification.ClassificationProcess


# Ensure unique class
class WhitespaceClassification(classification.ClassificationProcess.Classification):

    def process(self, statement: Statement) -> str:
        diffs = statement.object.definition.extensions["git"]

        if len(diffs) != 1:
            return None

        diff: Differential = diffs[0]

        if sum([sum([len(x[1:].strip()) for x in v.content]) for v in diff.parts]) == 0:
            return "WHITESPACE"

        if "editions" in statement.context.extensions:
            return

        n = 0

        for diff in diffs:

            for diffpart in diff.parts:

                key = (
                    statement.object.id
                    + "_"
                    + diff.file
                    + "_"
                    + str(diffpart.a_start_line)
                )

                if (
                    "insertions" in statement.context.extensions
                    and key in statement.context.extensions["insertions"]
                ):
                    insert = statement.context.extensions["insertions"][key]["content"]
                    n += len(insert) - len(insert.strip())

                if (
                    "deletions" in statement.context.extensions
                    and key in statement.context.extensions["deletions"]
                ):
                    delete = statement.context.extensions["deletions"][key]["content"]
                    n += len(delete) - len(insert.strip())

        if n > 0:
            return "WHITESPACE_CHANGE"

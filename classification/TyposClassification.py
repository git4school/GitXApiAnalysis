from tincan import *
from gittoxapi.differential import Differential, DiffPart


import classification.ClassificationProcess


# Ensure unique class
class TyposClassification(classification.ClassificationProcess.Classification):

    def process(self, statement: Statement) -> str:
        diffs: list[Differential] = statement.object.definition.extensions["git"]
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
                    if insert != None:
                        insert = insert.strip()

                    if insert == ";":
                        return "APPEND_SEMICOLUMN"

                if (
                    "deletions" in statement.context.extensions
                    and key in statement.context.extensions["deletions"]
                ):
                    delete = statement.context.extensions["deletions"][key]["content"]
                    if delete != None:
                        delete = insert.strip()

                    if delete == ";":
                        return "DELETE_SEMICOLUMN"

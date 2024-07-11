from tincan import *
from gittoxapi.differential import Differential, DiffPart


import classification.ClassificationProcess


# Ensure unique class
class AppendOrRemoveConditionClassification(
    classification.ClassificationProcess.Classification
):

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
                        insert = str(insert).strip()

                    if insert.startswith("&&") or insert.startswith("&&"):
                        return "APPEND_&&"
                    if insert.startswith("||") or insert.startswith("||"):
                        return "APPEND_||"
                    if insert == "!":
                        return "APPEND_!"

                if (
                    "deletions" in statement.context.extensions
                    and key in statement.context.extensions["deletions"]
                ):
                    delete = statement.context.extensions["deletions"][key]["content"]

                    if delete != None:
                        delete = str(delete).strip()

                    if delete.startswith("&&") or delete.endswith("&&"):
                        return "DELETE_&&"
                    if delete.startswith("||") or delete.endswith("||"):
                        return "DELETE_||"
                    if delete == "!":
                        return "DELETE_!"

                if "editions" in statement.context.extensions:
                    edit = statement.context.extensions["editions"][key]

                    before = str(edit["before"])
                    after = str(edit["after"])

                    if before.count("||") > after.count("||"):
                        return "REMOVED_||"

                    if before.count("&&") > after.count("&&"):
                        return "REMOVED_&&"

                    if before.count("||") < after.count("||"):
                        return "APPEND_||"

                    if before.count("&&") < after.count("&&"):
                        return "APPEND_&&"

                    if before.count("!") > after.count("!"):
                        return "REMOVED_&&"

                    if before.count("!") < after.count("!"):
                        return "APPEND_||"

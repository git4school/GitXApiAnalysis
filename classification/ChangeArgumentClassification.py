from tincan import *
from gittoxapi.differential import Differential, DiffPart


import classification.ClassificationProcess


# Ensure unique class
class ChangeArgumentClassification(classification.ClassificationProcess.Classification):

    def process(self, statement: Statement) -> str:
        diffs: list[Differential] = statement.object.definition.extensions["git"]
        for diff in diffs:

            for diffpart in diff.parts:
                content = diffpart.content

                key = (
                    statement.object.id
                    + "_"
                    + diff.file
                    + "_"
                    + str(diffpart.a_start_line)
                )

                if (
                    "editions" in statement.context.extensions
                    and key in statement.context.extensions["editions"]
                ):
                    edit = statement.context.extensions["editions"][key]

                    prefix = str(edit["prefix"]).strip()
                    suffix = str(edit["suffix"]).strip()

                    if prefix[-1] in ["(", ","] and suffix[0] in [")", ","]:
                        return "CHANGE_ARGUMENT"

                if (
                    "insertions" in statement.context.extensions
                    and key in statement.context.extensions["insertions"]
                ):
                    edit = statement.context.extensions["insertions"][key]

                    prefix = str(edit["prefix"]).strip()
                    content = edit["content"].strip()
                    suffix = str(edit["suffix"]).strip()

                    if prefix[-1] in ["(", ","] and suffix[0] in [")", ","]:
                        if "," in content:
                            return "APPEND_MULTIPLE_ARGUMENT"
                        else:
                            return "APPEND_ARGUMENT"
                if (
                    "deletions" in statement.context.extensions
                    and key in statement.context.extensions["deletions"]
                ):
                    edit = statement.context.extensions["deletions"][key]

                    prefix = str(edit["prefix"]).strip()
                    content = edit["content"].strip()
                    suffix = str(edit["suffix"]).strip()

                    if prefix[-1] in ["(", ","] and suffix[0] in [")", ","]:
                        if "," in content:
                            return "REMOVE_MULTIPLE_ARGUMENT"
                        else:
                            return "REMOVE_ARGUMENT"

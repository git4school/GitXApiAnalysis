from tincan import *
from gittoxapi.differential import Differential, DiffPart


import classification.ClassificationProcess


# Ensure unique class
class BooleanSwitchingClassification(
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

                if "editions" in statement.context.extensions:
                    edit = statement.context.extensions["editions"][key]

                    before = str(edit["before"]).strip().lower()
                    after = str(edit["after"]).strip().lower()

                    if before == "fals" and after == "tru":
                        return "SWITCH_FALSE_TO_TRUE"
                    if after == "fals" and before == "tru":
                        return "SWITCH_FALSE_TO_TRUE"

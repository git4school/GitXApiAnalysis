from tincan import *
from gittoxapi.differential import Differential, DiffPart
import regex

import classification.ClassificationProcess


# Does not ensure unique
class RefactoringClassification(classification.ClassificationProcess.Classification):

    def process(self, statement: Statement) -> str:

        if "refactoring" in statement.context.extensions:
            refactorings = statement.context.extensions["refactoring"]
            if refactorings != None and len(refactorings) > 0:
                return "REFACTORING"

        # diffs: list[Differential] = statement.object.definition.extensions["git"]
        # for diff in diffs:

        #     for diffpart in diff.parts:
        #         key = (
        #             statement.object.id
        #             + "_"
        #             + diff.file
        #             + "_"
        #             + str(diffpart.a_start_line)
        #         )

        #         if (
        #             "editions" in statement.context.extensions
        #             and key in statement.context.extensions["editions"]
        #         ):
        #             edit = statement.context.extensions["editions"][key]

        #             prefix = str(edit["prefix"])
        #             suffix = str(edit["suffix"])
        #             before = str(edit["before"])
        #             after = str(edit["after"])

        #             if prefix.endswith(" ") and suffix.startswith(" "):

        #                 if regex.match("^[a-zA-Z_$][\w$]*$", after) and regex.match(
        #                     "^[a-zA-Z_$][\w$]*$", before
        #                 ):
        #                     return "REFACTOR_RENAME"

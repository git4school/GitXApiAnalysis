from tincan import *
from gittoxapi.differential import Differential, DiffPart
import regex
from post_process import PostProcessModifier

import classification.ClassificationProcess


# Does not ensure unique
class RefactoringClassification(classification.ClassificationProcess.Classification):

    def process(self, statement: Statement) -> str:

        if "refactoring" in statement.context.extensions:
            refactorings = statement.context.extensions["refactoring"]
            if refactorings != None and len(refactorings) > 0:
                return "REFACTORING"

        if "git" in statement.object.definition.extensions:

            differentials: list[Differential] = statement.object.definition.extensions[
                "git"
            ]

            if all(
                [
                    all(
                        [
                            all(
                                [
                                    len(line[1:].strip()) == 0
                                    for line in part.content
                                    if len(line) >= 1
                                ]
                            )
                            for part in diff.parts
                            if part.content != None
                        ]
                    )
                    for diff in differentials
                    if diff.parts != None
                ]
            ):
                return "WHITESPACE"

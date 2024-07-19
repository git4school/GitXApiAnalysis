from tincan import *
from gittoxapi.differential import Differential, DiffPart


import classification.ClassificationProcess


class OneLinerClassification(classification.ClassificationProcess.Classification):

    def process(self, statement: Statement) -> str:
        id = statement.verb.id

        if not "git" in statement.object.definition.extensions:
            return

        differentials: list[Differential] = statement.object.definition.extensions[
            "git"
        ]
        if (
            all(
                [
                    all(
                        [
                            len(part.content) == 1
                            for part in diff.parts
                            if part.content != None
                        ]
                    )
                    for diff in differentials
                    if diff.parts != None
                ]
            )
            == 1
        ):
            return "ONE_LINE"

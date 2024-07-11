from tincan import *
from gittoxapi.differential import Differential, DiffPart


import classification.ClassificationProcess


# Ensure unique class
class StringEditionClassification(classification.ClassificationProcess.Classification):

    def process(self, statement: Statement) -> str:
        diffs = statement.object.definition.extensions["git"]

        if len(diffs) != 1:
            return None

        diff: DiffPart = diffs[0]

        parts = diff.parts

        editions = (
            statement.context.extensions["string_edition"]
            if "string_edition" in statement.context.extensions
            else []
        )

        if len(parts) != len(editions):
            return None

        return "STRING_EDITION"

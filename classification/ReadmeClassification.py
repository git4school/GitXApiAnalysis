from tincan import *
from gittoxapi.differential import Differential, DiffPart


import classification.ClassificationProcess


# Ensure unique class
class ReadmeClassification(classification.ClassificationProcess.Classification):

    def process(self, statement: Statement) -> str:
        diffs = statement.object.definition.extensions["git"]

        if len(diffs) != 1:
            return None

        diff: Differential = diffs[0]

        if diff.file == "README.md":
            return "README"

from tincan import *
from gittoxapi.differential import Differential, DiffPart


import classification.ClassificationProcess


# Ensure unique
class NaiveSystemEventClassification(
    classification.ClassificationProcess.Classification
):

    event_mapping = {
        "http://activitystrea.ms/schema/1.0/create": "FILE_CREATED",
        "http://activitystrea.ms/schema/1.0/delete": "FILE_DELETED",
        "resolved": "QUESTION_FIXED",
    }

    def process(self, statement: Statement) -> str:
        id = statement.verb.id

        if id in self.event_mapping:
            return self.event_mapping[id]

        if id == "http://curatr3.com/define/verb/edited":
            diffs: list[Differential] = statement.object.definition.extensions["git"]

            amounts_of_parts = sum([len(d.parts) for d in diffs])

            if amounts_of_parts == 0:
                return "METADATA_EDITION"

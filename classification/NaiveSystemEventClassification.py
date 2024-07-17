from tincan import *
from gittoxapi.differential import Differential, DiffPart


import classification.ClassificationProcess


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

        if id in self.event_mapping.keys():
            statement.context.extensions["atomic"] = True
            o = self.event_mapping.get(id)
            return o

        if id == "http://curatr3.com/define/verb/edited":
            diffs: list[Differential] = statement.object.definition.extensions["git"]

            amounts_of_parts = sum(
                [len(d.parts) for d in diffs if d.file.endswith(".java")]
            )

            if amounts_of_parts == 0:
                statement.context.extensions["atomic"] = True
                return "METADATA_EDITION"

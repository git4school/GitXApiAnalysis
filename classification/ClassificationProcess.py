from tincan import *
from gittoxapi.differential import Differential, DiffPart


class Classification:
    def __init__(self) -> None:
        pass

    def process(self, statement: Statement) -> str:
        return None

    def classify(self, statement: Statement) -> bool:
        found_class = None

        try:
            found_class = self.process(statement)
        except Exception:
            return False

        if found_class == None:
            return False

        statement.context.extensions["classified"].append(found_class)

        return True

from tincan import *
from gittoxapi.differential import Differential, DiffPart


class PostProcessModifier:
    def __init__(self) -> None:
        pass

    def level(self):
        pass

    def _process(self, statement: Statement, **kargs):
        pass

    def process(self, statement: Statement):

        if self.level() == Verb:
            self._process(statement=statement, verb=statement.verb)
        elif self.level() == DiffPart:

            for differential in statement.object.definition.extensions["git"]:
                differential: Differential = differential

                if differential == None or differential.parts == None:
                    continue

                for part in differential.parts:
                    self._process(
                        statement=statement, differential=differential, diffpart=part
                    )

        elif self.level() == Statement:
            self._process(statement=statement)

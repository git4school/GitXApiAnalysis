from typing import Callable
from tincan import Statement, Verb
from modifier.StatementModifier import StatementModifier


class PreciseVerbModifier(StatementModifier):

    event_mapping = {
        "[modified]": "http://curatr3.com/define/verb/edited",
        "[created]": "http://activitystrea.ms/schema/1.0/create",
        "[deleted]": "http://activitystrea.ms/schema/1.0/delete",
        "Fix": "resolved",
    }

    def process_statement(self, st_getter: Callable[[int], Statement | None], i: int):
        statement = st_getter(i)

        verb = statement.verb
        description = str(statement.object.definition.description["en-US"])

        for s in self.event_mapping:
            if description.startswith(s):
                verb.id = self.event_mapping[s]

                description = description[len(s + " ") :]
                statement.object.definition.description["en-US"] = description

        if (
            not ("git" in statement.object.definition.extensions)
            or len(statement.object.definition.extensions["git"]) == 0
        ):
            return [statement]

        if all([git.added for git in statement.object.definition.extensions["git"]]):
            verb.id = self.event_mapping["[created]"]

        if all([git.deleted for git in statement.object.definition.extensions["git"]]):
            verb.id = self.event_mapping["[deleted]"]

        return [statement]

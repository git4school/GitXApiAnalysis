from post_process.PostProcessModifier import PostProcessModifier
from tincan import Statement, Verb


class PreciseVerb(PostProcessModifier):

    event_mapping = {
        "[modified]": "http://curatr3.com/define/verb/edited",
        "[created]": "http://activitystrea.ms/schema/1.0/create",
        "[deleted]": "http://activitystrea.ms/schema/1.0/delete",
        "Fix": "resolved",
    }

    def level(self):
        return Verb

    def _process(self, statement: Statement, verb: Verb, **kargs):
        description = str(statement.object.definition.description["en-US"])

        for s in self.event_mapping:
            if description.startswith(s):
                verb.id = self.event_mapping[s]

                description = description[len(s + " ") :]
                statement.object.definition.description["en-US"] = description

        if all([git.added for git in statement.object.definition.extensions["git"]]):
            verb.id = self.event_mapping["[created]"]

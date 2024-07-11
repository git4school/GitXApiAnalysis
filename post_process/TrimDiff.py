from post_process.PostProcessModifier import PostProcessModifier
from gittoxapi.differential import DiffPart
from tincan import Statement, Verb


class TrimDiff(PostProcessModifier):
    def level(self):
        return DiffPart

    def _process(self, statement: Statement, diffpart: DiffPart, **kargs):
        content = diffpart.content
        real_content = [i for i in range(len(content)) if content[i][0] != " "]
        start_shift = min(real_content)
        end_shift = max(real_content)
        content = [
            v
            for (v, i) in zip(content, range(len(content)))
            if start_shift <= i <= end_shift
        ]

        diffpart.content = content
        diffpart.a_start_line += start_shift
        diffpart.a_interval = len([v for v in content if v[0] != "-"])
        diffpart.b_start_line += start_shift
        diffpart.b_interval = len([v for v in content if v[0] != "+"])

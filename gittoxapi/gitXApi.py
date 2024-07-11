from dateutil.utils import today
import dateutil.tz
from git import Repo, Diff, Commit
from git.compat import defenc
from tincan import (
    Statement,
    Context,
    Activity,
    Agent,
    Verb,
    Extensions,
    LanguageMap,
    ActivityDefinition,
)

from gittoxapi.differential import Differential, DiffPart


def diff_to_obj(diff: Diff) -> Differential:
    """Turn git diff to Differential (the xApi extension which manage git diff)

    Args:
        diff (Diff): The commit diff to transform

    Returns:
        Differential: The differential object which match exactly a git diff object (except score field)
    """
    content = Differential()

    h = "%s"
    if diff.a_blob:
        h %= diff.a_blob.path
    elif diff.b_blob:
        h %= diff.b_blob.path
    content.file = h

    if diff.deleted_file:
        content.deleted = True
    if diff.new_file:
        content.added = True
    if diff.copied_file:
        content._copied = [diff.b_path, diff.a_path]
    if diff.rename_from:
        content.renamed_from = diff.rename_from
    if diff.rename_to:
        content.renamed_to = diff.rename_to
    if diff.diff:
        try:

            raw = (
                diff.diff.decode(defenc) if isinstance(diff.diff, bytes) else diff.diff
            )

            if not "@@ -" in raw:
                return content

            raw = raw.split("\n@@ -")
            parts = []
            diffs = []

            for l in raw:
                if not l.startswith("@@ -"):
                    l: str = "@@ -" + l

                lines = l.splitlines()

                positions = lines[0].split("@@")[1][1:-1].split(" ")
                a_start_line, a_interval = positions[0][1:].split(",")
                b_start_line, b_interval = (positions[1][1:].split(",") + ["1"])[:2]

                part = DiffPart()
                part.a_start_line

                parts.append(part)
                part.a_start_line = int(a_start_line)
                part.a_interval = int(a_interval)
                part.b_start_line = int(b_start_line)
                part.b_interval = int(b_interval)
                part.content = lines[1:]

            content.parts = parts

            return content
        except UnicodeDecodeError:
            msg += "OMITTED BINARY DATA"

    return content


def commit_to_stmt(
    commit: Commit, before: any = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"
) -> Statement:
    """
    Turn git commit to xApi statement

    Args:
        commit (Commit): The git Commit to create statement for
        before (any, optional): Defaults to "4b825dc642cb6eb9a060e54bf8d69288fbee4904". The commit before or the initial empty commit if none is provided

    Returns:
        _type_: Statement The xAPI statement
    """
    stmt = Statement()
    stmt.timestamp = commit.authored_date
    stmt.stored = today(tzinfo=dateutil.tz.gettz())

    stmt.actor = Agent()
    stmt.actor.name = commit.author.name
    stmt.actor.mbox = commit.author.email

    stmt.verb = Verb()
    stmt.verb.id = "http://curatr3.com/define/verb/edited"

    stmt.object = Activity()
    stmt.object.object_type = "http://id.tincanapi.com/activitytype/code-commit"
    stmt.object.id = commit.hexsha
    stmt.object.definition = ActivityDefinition()
    stmt.object.definition.description = LanguageMap()
    stmt.object.definition.description["en-US"] = commit.message.strip()

    diff = commit.diff(before, create_patch=True, R=True)

    stmt.object.definition.extensions = Extensions()
    stmt.object.definition.extensions["git"] = [diff_to_obj(v) for v in diff]

    stmt.context = Context()
    return stmt


def generate_xapi(repo: Repo) -> list[Statement]:
    """_summary_ Generate list of statements with each statement that represent a commit and its diff with the commit before"""
    commits = list(repo.iter_commits())

    # The first initial commit is the empty one, this is its hash (its the same accross all git repositories)
    before = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"

    stmts = []
    for current in commits[::-1]:
        stmts.append(commit_to_stmt(current, before))
        before = current
    return stmts


def deserialize_definition_extension_for_all(l: list[Statement], id: str, cons: any):
    for s in l:
        deserialize_definition_extension(s, id, cons)


def deserialize_definition_extension(s: Statement, id: str, cons: any):
    s.object.definition.extensions[id] = cons(s.object.definition.extensions[id])


def deserialize_context_extension_for_all(l: list[Statement], id: str, cons: any):
    for s in l:
        deserialize_context_extension(s, id, cons)


def deserialize_context_extension(s: Statement, id: str, cons: any):
    s.object.context.extensions[id] = cons(s.object.definition.extensions[id])

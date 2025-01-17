import json
import GitToXApi.utils
from tincan import Statement
import GitToXApi.differential
from GitToXApi.utils import *
from tincan import Context
import copy
from identifier import *
from modifier import *
import debug
import shutil
import os
from xes_file import *
import argparse
import subprocess


def format_statement(st: Statement) -> Statement:
    if st.context == None:
        st.context = Context()

    if st.context.extensions == None:
        st.context.extensions = dict()

    return st


def exec_modifier(statements: list[Statement], identifier: CodeModifier):
    st_getter = lambda x: statements[x] if 0 <= x < len(statements) else None
    processed = {}
    i = 0
    while i < len(statements):
        st: Statement = st_getter(i)
        if TaskIdentifier.is_task_set(st) and isinstance(
            identifier, ActivityIdentifier
        ):
            i += 1
            continue
        last_id = st.object.id
        if last_id in processed:
            i += 1
            continue
        processed[last_id] = True
        try:
            returns = identifier.process_statement(st_getter, i)
        except:
            print("Error occured in", st.object.id)
            raise Exception
        statements = statements[:i] + returns + statements[i + 1 :]

    return statements


def dump(
    name: str,
    out: str,
    statements: list[Statement],
    filter: Callable[[Statement], bool],
) -> None:
    with open(out + name + ".json", "w") as f:
        f.write(
            json.dumps(
                [stmt.as_version() for stmt in statements if filter(stmt)],
                indent=2,
            )
        )


def generate_files(repo: Repo, out_folder, repo_name: str):
    repo_path = repo.git_dir[: repo.git_dir.rindex("/")]
    print("Getting files for", repo_path)

    dest_xapi = out_folder + repo_name + ".json"
    if not os.path.exists(dest_xapi):
        stmts = GitToXApi.utils.generate_xapi(repo, {"unified": 1000})

        print("Generation of xapi files for", repo_path)
        with open(dest_xapi, "w") as f:
            f.write(GitToXApi.utils.serialize_statements(stmts, indent=2))

    dest_refactoring = out_folder + repo_name + "_refactoring.json"
    if not os.path.exists(dest_refactoring):
        print("Generation of refactoring files for", repo_path)
        subprocess.run(
            "RefactoringMiner -a " + repo_path + " -json " + dest_refactoring,
            shell=True,
            capture_output=True,
        )

    print("Files where collected for", repo_path)


def identify_task(path: str, out: str, full_log: bool = False):

    repo_name = path[path.rfind("/") + 1 : path.rfind(".")]
    refactoring_file = path[: path.rfind(".")] + "_refactoring.json"

    initial_statements = None
    with open(path) as f:
        initial_statements = deserialize_statements(f)
    initial_statements = [format_statement(s) for s in initial_statements]
    initial_total = len(initial_statements)
    statements = copy.deepcopy(initial_statements)

    code_modifiers = [
        PreciseVerbModifier(),
        NotSourceTask(),
        RefactoringMinerTask(refactoring_file),
        TrimEditionContentModifier(),
        LineBreakAndSpacingChangeTask(),
        CutPasteTask(),
        EditionDetectionModifier(),
        CodeEditionIdentifier(),
        PackageTask(),
        ImportTask(),
        ClassTask(),
        FunctionTask(),
        AnnotationTask(),
        EmptyLineChangeTask(),
        ForTask(),
        IfTask(),
        ReturnTask(),
        VariableDeclarationTask(),
        MethodInvocationTask(),
        BlockTask(),
        SyntaxTypo(),
        MarkCompleted(),
    ]

    code_modifiers += [
        RemoveEmptyCodePartModifier(),
        RemoveEmptyDifferentialModifier(),
        EmptyGitTaskIdentifier(),
        NamePathModifier(),
    ]

    for modif in code_modifiers:
        statements = exec_modifier(statements, modif)

    scores = {"UNKNOWN": 0}

    for st in statements:
        if TaskIdentifier.is_task_set(st):
            task = TaskIdentifier.get_task(st)[0]
            if not task in scores:
                scores[task] = 0
            scores[task] += 1
        else:
            scores["UNKNOWN"] += 1

    if full_log:
        for k in scores:
            if k in debug.CLASS_MASK:
                continue
            safe_name: str = k.lower().replace(" ", "_")
            dump(
                safe_name,
                out,
                statements,
                lambda x: "task" in x.context.extensions
                and x.context.extensions["task"]["id"] == k,
            )
        dump(
            "unknown",
            out,
            statements,
            lambda x: not "task" in x.context.extensions,
        )

    if full_log:
        dump(repo_name + "_task", out, statements, lambda x: True)

    with open(out + repo_name + "_compressed.json", "w") as f:
        f.write(
            json.dumps(
                [
                    (
                        dict(stmt.context.extensions)
                        | {"id": stmt.object.id}
                        | {"timestamp": st.timestamp.timestamp()}
                        | {"verb": st.verb.id}
                    )
                    for stmt in statements
                ],
                indent=2,
            )
        )

    scores = [(k, scores[k]) for k in scores]
    scores.sort(key=lambda v: -v[1])

    [
        print(k, v, (str(v * 100 / len(statements)) + "    ")[:4], "%")
        for (k, v) in scores
    ]

    if debug.GENERATE_XES_FROM_INITIAL:
        generate_xes_from_initial(
            initial_statements, statements, out=out + "initial.xes"
        )

    if debug.GENERATE_XES_FROM_CREATED:
        generate_xes_from_created(statements, out=out + "created.xes")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="GitXApiAnalysis",
        description="Program used to analyze git xapi files",
    )

    parser.add_argument("filename")
    parser.add_argument(
        "--generate", "-g", action=argparse.BooleanOptionalAction, default=False
    )
    parser.add_argument("-o", "--out", default="")
    parser.add_argument(
        "-l", "--log", action=argparse.BooleanOptionalAction, default=False
    )
    parser.add_argument(
        "-d", "--dir", action=argparse.BooleanOptionalAction, default=False
    )

    args = parser.parse_args()

    filename = args.filename
    generate = args.generate
    out_folder = args.out
    log = args.log
    dir = args.dir

    if out_folder != "" and out_folder[-1] != "/":
        out_folder += "/"
    if filename[-1] == "/":
        filename = filename[:-1]

    if out_folder != "" and not os.path.exists(out_folder):
        os.makedirs(out_folder)

    if not os.path.exists(filename):
        raise FileNotFoundError(filename)

    if dir:
        for f in os.listdir(filename):

            if generate:
                if not os.path.exists(filename + "/" + f + "/.git"):
                    print("Ignore", f, "because it does not contains .git")
                    continue
                repo = Repo(filename + "/" + f)
                print(filename + "/" + f)
                generate_files(repo, out_folder, f)
            else:
                if not "." in f:
                    continue
                f = f[: f.rfind(".")]
                path = filename + "/" + f + ".json"
                name = path[path.rfind("/") + 1 : path.rfind(".")]
                if os.path.exists(filename + "/" + f + "_refactoring.json"):
                    print(filename + "/" + f)
                    identify_task(
                        filename + "/" + f + ".json", out_folder, full_log=log
                    )
    else:
        if generate:
            repo = Repo(filename)
            generate_files(
                repo, out_folder, ("/" + filename)[("/" + filename).rfind("/") + 1 :]
            )
        else:
            identify_task(filename, out_folder, full_log=log)

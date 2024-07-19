from tincan import *
from gittoxapi.differential import Differential, DiffPart
import regex

import classification.ClassificationProcess


class AddBodyClassification(classification.ClassificationProcess.Classification):

    def process(self, statement: Statement) -> str:

        if not "git" in statement.object.definition.extensions:
            return

        differentials: list[Differential] = statement.object.definition.extensions[
            "git"
        ]

        if len(differentials) != 1 or differentials[0].parts == None:
            return

        diff = differentials[0]
        if len(diff.parts) > 1 or len(diff.parts[0].content) <= 1:
            return
        content = diff.parts[0].content
        addition = False

        content = [
            l
            for l in content
            if len(l[1:].strip()) != 0 and not l[1:].strip().startswith("@")
        ]
        if not (
            all([l[0] == "+" for l in content]) or all([l[0] == "-" for l in content])
        ):
            return

        addition = content[0][0] == "+"
        content = [l[1:] for l in content]

        last_line = content[-1].replace("\t", " ")

        if last_line.strip() == "}":
            first_line = content[0].replace("\t", " ")
            if (
                regex.match(
                    " *((public|private|protected) +|)[a-zA-Z0-9_]+ +[a-zA-Z0-9_]+( )*\\(",
                    first_line,
                )
                != None
            ):
                return "ADD_FUNCTION" if addition else "REMOVE_FUNCTION"

            lines = [
                e
                for e in content
                if not (
                    e.startswith("import") or e.startswith("package") or e.strip() == ""
                )
            ]

            if len(lines) > 0:
                class_line = lines[0]

                if (
                    regex.match(
                        " *class [a-zA-Z-0-9_]+",
                        class_line,
                    )
                    != None
                ):
                    return "ADD_CLASS" if addition else "REMOVE_CLASS"

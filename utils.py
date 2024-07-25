import javalang


def find_delim(lines: list[str], begin_col: int = None, begin_row: int = 0, delim="{"):

    delims = {"{": "}", "(": ")", "[": "]", "<": ">"}

    assert delim in delims

    begin_delim = delim
    end_delim = delims[delim]

    assert begin_col == None or lines[begin_row][begin_col] == begin_delim

    still_opened = 0 if begin_col == None else 1
    for line_i, line in zip(range(begin_row, len(lines)), lines[begin_row:]):
        if line_i == begin_row:
            line: str = line[(begin_col + 1) if begin_col != None else 0 :]
        if line.count(end_delim) < still_opened:
            still_opened -= line.count(end_delim)
            still_opened += line.count(begin_delim)
        else:
            for c_i, c in zip(range(len(line)), line):
                if c == begin_delim:
                    if begin_col == None:
                        begin_row = line_i
                        begin_col = c_i
                    still_opened += 1
                elif c == end_delim and begin_col != None:
                    still_opened -= 1
                if still_opened == 0 and begin_col != None:
                    return [
                        (begin_row, begin_col),
                        (line_i, c_i + (begin_col if (begin_row == line_i) else 0)),
                    ]

    return None


def tokenize(s: str) -> list[str]:
    tokens = list(javalang.tokenizer.tokenize(s, ignore_errors=True))
    return [(v.value, v.position, type(v).__name__, type(v)) for v in tokens]


def find_token_substitution(s1: str, s2: str):
    IDENTIFIER_NAME = javalang.tokenizer.Identifier.__name__
    LITTERAL = []

    s1_tokens = tokenize(s1)
    s2_tokens = tokenize(s2)

    LITTERAL += [
        v[2] for v in s1_tokens if issubclass(v[3], javalang.tokenizer.Literal)
    ]

    LITTERAL += [
        v[2] for v in s2_tokens if issubclass(v[3], javalang.tokenizer.Literal)
    ]

    LITTERAL = set(LITTERAL)

    if len(s1_tokens) != len(s2_tokens):
        return

    if not all(
        (s1_tokens[i][2] == s2_tokens[i][2])
        or (s1_tokens[i][2] == IDENTIFIER_NAME or s1_tokens[i][2] in LITTERAL)
        or (s2_tokens[i][2] == IDENTIFIER_NAME or s2_tokens[i][2] in LITTERAL)
        for i in range(len(s1_tokens))
    ):
        return

    def is_equal(subst_origin, subs_dest):
        identifier_subst = subst_origin[2] == subs_dest[2] == IDENTIFIER_NAME

        for i in range(len(s1_tokens)):
            if s1_tokens[i][2] == s2_tokens[i][2] == IDENTIFIER_NAME:
                if identifier_subst:
                    if not (
                        (
                            s1_tokens[i][0] == subst_origin[0]
                            and s2_tokens[i][0] == subs_dest[0]
                        )
                        or (s1_tokens[i][0] == s2_tokens[i][0])
                    ):
                        return False
                elif s1_tokens[i][0] != s2_tokens[i][0]:
                    return False

            elif s1_tokens[i][2] == IDENTIFIER_NAME:
                if not (
                    subst_origin[2] == IDENTIFIER_NAME
                    and subst_origin[0] == s1_tokens[i][0]
                    and s2_tokens[i][0] == subs_dest[0]
                ):
                    return False
            elif s2_tokens[i][2] == IDENTIFIER_NAME:
                if not (
                    subs_dest[2] == IDENTIFIER_NAME
                    and subs_dest[0] == s2_tokens[i][0]
                    and s1_tokens[i][0] == subst_origin[0]
                ):
                    return False
        return True

    # filter identifiers
    s1_substituable = [
        v for v in s1_tokens if v[2] == IDENTIFIER_NAME or v[2] in LITTERAL
    ]
    s2_substituable = [
        v for v in s2_tokens if v[2] == IDENTIFIER_NAME or v[2] in LITTERAL
    ]

    if len(s1_substituable) != len(s2_substituable):
        return

    for i in range(len(s1_substituable)):
        if is_equal(s1_substituable[i], s2_substituable[i]):
            s1_value, s1_pos, s1_type_name, s1_type = s1_substituable[i]
            s2_value, s2_pos, s2_type_name, s2_type = s2_substituable[i]
            return (
                (s1_value, s1_type, s1_type_name in LITTERAL),
                (s2_value, s2_type, s2_type_name in LITTERAL),
            )

    return

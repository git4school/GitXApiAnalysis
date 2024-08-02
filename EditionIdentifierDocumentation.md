# Edition Identifier Documentation

Classification is done in order, if an edition is matched against one of the class above it won't be classified by what's under

Stripping a string is removing all starting and ending spaces, tabulations or new line.

## Variable and functions used

### Arguments

- prefix : common prefix
- before : content before
- after : content after
- suffix : common suffix
- tags : a list of previously computed tags
  - "INSERT" : if stripped before is empty
  - "DELETE" : if stripped after is empty
  - "STRING" : if change occurs in a quoted string constant
  - "COMMENT" : if change involve comment
  - "WORD_EDIT" : if stripped before and stripped after do not contains space

### Variables

Pre computed variables are :

- strip_prefix : stripped prefix
- strip_before : stripped before
- strip_after : stripped after
- strip_suffix : stripped suffix
- before_line : prefix + before + suffix
- after_line : prefix + after + suffix

### Functions

We dispose of two functions :

- is\_added(raw) : raw content was not in the line before and is in the line after
- is\_removed(raw) : raw conta    nt was in the line beofre and is no longer in the line after

## Documentation

### Comment

If `COMMENT` tag is present the edition is only about comment and so we use `is\_added` and `is\_removed` to differentiate :

- COMMENT_ADDITION : is\_added("//")
- COMMENT_DELETION : is\_removed("//")
- COMMENT_MOVED : (is\_removed("/\*") or is\_added("/\*") and not "*/" in after) or (is\_removed("*/") or is\_added("*/") and not "/\*" in after)
- COMMENT_EDITION : if none other match

### Token

We use a function located in `utils.py` to compute singleton token substitution from before_line to after_line

Then we check for three different cases :

- RENAME\_VARIABLE : if change consist of renaming a variable during it's assignation
- CHANGE\_VARIABLE_USED : if change consist of renaming a variable
- CHANGE\_METHOD_INVOCATED : if change consist of changing a method invocated
- CHANGE\_LITTERAL_VALUE : if change is only modifying litteral value (0 -> 1, true -> false, "Hello" -> "hello")
- LITTERAL\_TO\_VARIABLE : if change consists of replacing a litteral with a variable
- VARIABLE\_TO\_LITTERAL : if change consists of replacing a variable with a litteral

### String

We do not precisely check for differences in string, for now we classify all cases where the STRING tag is present to STRING\_EDITION

### Insertions

When INSERT tag is present we differentiate  :

- ADD_RETURN_VALUE : if `return` statement is added
- ADD_VARIABLE_VALUE : if the change is an addition of a variable value (v = -> v = 1;)
- MODIFY_VARIABLE_VALUE : if the change only occurs inside the value

### Typo

We defined a typo as change of only one character added or removed.

We detect two different types of typos :

- TYPO_ADD : one character is inserted
- TYPO_DEL : one character is removed

### Word edition

Whe 'WORD-EDIT' tag is present we differentiate :

- REPLACE_METHOD : if change occurs between a '.' and a '('
- REPLACE_FUNCTION : if change occurs between a ' ' and a '('
- RENAME_FUNCTION : if change occurs in a function header

### Assignments

We differentiate :

- ASSIGN_VARIABLE : strip\_after starts with a "=" and not a "=="
- UNASSIGN_VARIABLE : strip\_before starts with a "=" and not a "=="

### Array index

We detect change (CHANGE_ARRAY_INDEX) array index if edition takes place inside "[" "]".

### Condition

We detect change (CONDITION) if edition takes place inside a loop condition or a if, else if, switch.

### Variable use and rename

We detect :

- USE_OLD_VARIABLE : if "int a = 2" is changed to "b = 2" (type is removed)
- USE_OLD_VARIABLE : if "a = 2" is changed to "int b = 2" (type is added)
- RENAME : if type is present but name is changed
- CHANGE_VARIABLE_VALUE : if the change is in the variable value

### Function parameter

When change occurs inside parantheses we detect :

- ADD_FUNCTION_PARAMETER : if change is an insertion and contains a comma
- REMOVE_FUNCTION_PARAMETER : if change is a deletion and contains a comma
- EDIT_FUNCTION_PARAMETERS : in other cases

### Return change

We detect :

- EDIT_RETURN_VALUE : when the line is a return line and changes occurs in the return value

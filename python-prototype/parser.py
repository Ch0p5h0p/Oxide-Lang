'''
GOALS
1. Create meaning, relate tokens together into expressions while also checking validity (you can't add a num to a str)
    Ex: the sequence VAL-NUM(a) INLINE_OP(+) VAL-NUM(b) should become something like APPLY(ADD(A,B))
2. Resolve function calls with no hanging variables.
    Ex: a function called as ADD(1,2) should be reduced to 3, but a function called as ADD(1,x) should not be reduced.
3. Generate AST
4. Prune unreachable branches of the AST
'''
class Parser:
    def __init__(self, tokens):
        self.tokens=tokens
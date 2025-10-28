from lexer import Lexer, TOKENTYPES
from resolver import Resolver, DEFS

c='"Hello, world"("here\'s a tiny group with no space") [have an array] {and an expression} (+={this[is+a (test)]}) "and this is another one"'
l=Lexer(c)
print("Lexing")
r=Resolver(l.lex())
print("Resolving")
r.resolveTokens()
print(r)
"""
EXPECTED:
STR [LETTER Hello | DELIM , | LETTER world]
GROUP [
    VAL LETTER this | GROUP [
        VAL LETTER is | VAL LETTER a | GROUP [
            VAL LETTER test
        ]
    ]
]
"""
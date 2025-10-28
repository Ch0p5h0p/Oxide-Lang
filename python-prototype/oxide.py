from lexer import Lexer, TOKENTYPES
from resolver import Resolver, DEFS

c='"Hello, world" {this[is a (test)]}'
l=Lexer(c)
r=Resolver(l.lex())
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
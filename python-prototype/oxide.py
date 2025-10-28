from lexer import Lexer, TOKENTYPES
from resolver import Resolver, DEFS

# Yes, I know this test string is bad. No, I don't regret it. No, I'm not going to change it :P
c='"Hello, world"("here\'s a group with no leading space") [have an array] {and an expression}a=b (+={this[is+a (test)]})"and this is another one"'

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
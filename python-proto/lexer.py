class TOKENS:
    operators=[*"+-*/"]
    letters=[*"qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM"]
    digits=[*"1234567890"]
    delims=[*"{}[]()\'\""]
    special=[*".;"]

class Lexer:
    def __init__(self, code):
        self.code=code
        self.i=0
        self.tokens=[]
    
    def lex(self):
        while True:
            #print(f"LEXER: {self.i:<3} | TOKENS: {self.tokens}")
            current=self.code[self.i]
            if current in TOKENS.operators:
                self.lexType("operator")
            elif current in TOKENS.digits:
                self.lexType("digit")
            elif current in TOKENS.letters:
                self.lexType("string")
            elif current in TOKENS.delims:
                self.lexType("delim")
            elif current in TOKENS.special:
                self.lexType("special")
            self.i+=1
            if self.i>=len(self.code):
                break
        return self.tokens

    def lexType(self,t):
        if t=="operator":
            self.tokens.append(("OPERATOR",self.code[self.i]))
        elif t=="digit":
            buffer=[]
            j=0
            while self.code[self.i+j] in TOKENS.digits:
                buffer.append(self.code[self.i+j])
                j+=1
            self.tokens.append(("NUM","".join(buffer)))
            self.i+=j-1
        elif t=="string":
            buffer=[]
            j=0
            while self.code[self.i+j] in TOKENS.letters:
                buffer.append(self.code[self.i+j])
                j+=1
            self.tokens.append(("STR","".join(buffer)))
            self.i+=j-1
        elif t=="delim":
            self.tokens.append(("DELIM",self.code[self.i]))
        elif t=="special":
            self.tokens.append(("SPECIAL",self.code[self.i]))
    
    def __str__(self):
        return f"\"{self.code}\" -> {self.tokens}"

c="1234.abcd ({[]}) +/-* 123+abc *12b63;"
'''
EXPECTED:
NUM 1234
STR abcd
DELIM (
DELIM {
DELIM [
DELIM ]
DELIM }
DELIM )
OPERATOR +
OPERATOR /
OPERATOR -
OPERATOR *
NUM 123
OPERATOR +
STR abc
OPERATOR *
NUM 12
STR b
NUM 63
BREAK
'''
l=Lexer(c)
t=l.lex()
print(l)

out=r""
for i in t:
    out+=i[1]
    out+=" "

print(out)
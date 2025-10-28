class TOKENTYPES:
    operators=[*"+-*/="]
    letters=[*"qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM"]
    digits=[*"1234567890"]
    delims=[*"{}[]()\'\","]
    special=[*".;"]
    hint=[*":"]

class Lexer:
    def __init__(self, code):
        self.code=code
        self.i=0
        self.tokens=[]
    
    def lex(self):
        while True:
            #print(f"LEXER: {self.i:<3} | TOKENS: {self.tokens}")
            current=self.code[self.i]
            if current in TOKENTYPES.operators:
                self.lexType("operator")
            elif current in TOKENTYPES.digits:
                self.lexType("digit")
            elif current in TOKENTYPES.letters:
                self.lexType("letters")
            elif current in TOKENTYPES.hint:
                self.lexType("hint")
            elif current in TOKENTYPES.delims:
                if current=="\"" or current=="\'":
                    self.lexType("string")
                else:
                    self.lexType("delim")
            elif current in TOKENTYPES.special:
                self.lexType("special")
            self.i+=1
            if self.i>=len(self.code):
                break
        return self.tokens

    def lexType(self,t):
        #print(f"{self.i}: {self.code[self.i]} ({t})")
        if t=="operator":
            if self.i<(len(self.code)-1) and self.code[self.i+1]=="=":
                self.tokens.append(("OPERATOR",self.code[self.i]+"="))
                self.i+=1
            else:
                self.tokens.append(("OPERATOR",self.code[self.i]))
        elif t=="digit":
            buffer=[]
            j=0
            while self.code[self.i+j] in TOKENTYPES.digits:
                buffer.append(self.code[self.i+j])
                j+=1
            self.tokens.append(("NUM","".join(buffer)))
            self.i+=j-1
        elif t=="letters":
            buffer=[]
            j=0
            while self.code[self.i+j] in TOKENTYPES.letters:
                buffer.append(self.code[self.i+j])
                j+=1
                if self.i+j==len(self.code): break
            self.tokens.append(("LETTERS","".join(buffer)))
            self.i+=j-1
        elif t=="hint":
            self.tokens.append(("HINT",self.code[self.i+1:self.i+4]))
            self.i+=3
        elif t=="string":
            buffer=""
            quote=self.code[self.i]
            j=1
            while True:
                if self.code[self.i+j]==quote:
                    break
                else:
                    buffer+=self.code[self.i+j]
                    j+=1
            self.tokens.append(("STR",buffer))
            self.i+=j
        elif t=="delim":
            self.tokens.append(("DELIM",self.code[self.i]))
        elif t=="special":
            self.tokens.append(("SPECIAL",self.code[self.i]))
    
    def __str__(self):
        return f"\"{self.code}\" -> {self.tokens}"

if __name__=="__main__":
    c="1234.abcd ({[]}) +/-* 123+abc *12b63;"
    '''
    EXPECTED:
    NUM 1234
    LETTER abcd
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
    LETTER abc
    OPERATOR *
    NUM 12
    LETTER b
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
class DEFS:
    keywords=["df","ret","if","else"]
    openers=[*"({["]
    closers=[*")}]"]
    strdelims=[*"\"\'"]

class Resolver:
    def __init__(self, tokens):
        self.tokens=tokens
        self.i=0
        self.resolved=[]
        self.recurse_count=0

    def resolveTokens(self):
        while True:
            if self.i>=len(self.tokens):
                break
            current=self.tokens[self.i]
            print(current)
            #print(f"{self.i}/{len(self.tokens)}")
            if current[1] in DEFS.keywords:
                self.resolved.append(("KW", current))
            elif current[0]=="OPERATOR":
                self.resolved.append(("INLINE_OP", current))
            elif current[1] in DEFS.openers:
                self.recurse_count+=1
                group=self.parseGroup(self.tokens[self.i:])
                self.resolved.append(group[0])
                self.i+=group[1]
            elif current[1] in DEFS.closers:
                raise Exception(f"Resolver error: hanging closing delimiter {current[1]}")
            else:
                self.resolved.append(("VALUE",self.tokens[self.i]))
            self.i+=1

    def parseGroup(self, toks):
        #print("Opening group")
        j=1
        buffer=[]
        opener=toks[0][1]
        closer=DEFS.closers[DEFS.openers.index(opener)]
        #print(f"O:{opener} C:{closer}")
        t="GROUP"
        if opener=="(":
            t="GROUP"
        elif opener=="{":
            t="EXPR"
        elif opener=="[":
            t="ARR"
        while True:
            print(f"{'|'*self.recurse_count}{toks[j]}")
            if toks[j][1] in DEFS.openers:
                self.recurse_count+=1
                group=self.parseGroup(toks[j:])
                buffer.append(group[0])
                j+=group[1]
            elif toks[j][1]==closer:
                #print("Closing group")
                self.recurse_count-=1
                return (t, buffer), j
            elif toks[j][1] in DEFS.keywords:
                buffer.append(("KW",toks[j]))
            elif toks[j][0]=="OPERATOR":
                buffer.append(("INLINE_OP",toks[j]))
            else:
                buffer.append(("VAL",toks[j]))
            j+=1

    def __str__(self):
        return f"{self.resolved}"
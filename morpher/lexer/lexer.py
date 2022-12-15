from typing import List
COMMENTS_STARTER = "--"
CONTINUE_SYMBOL = "\t"
PARTS_SPLITTER = " . "
TOKENS_SPLITTER = " "

PARTS_SPLITTER_TOKEN = "DOT"

class Token:
    def __init__(self, s: str):
        self.token = s 

    def __repr__(self) -> str:
        return "TOKEN: {}".format(self.token)

    def __call__(self) -> str:
        return self.token

class Dot(Token):
    def __init__(self):
        super().__init__(PARTS_SPLITTER_TOKEN)
    
    def __repr__(self) -> str:
        return PARTS_SPLITTER_TOKEN

class Part:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens

    def __getitem__(self, i) -> str:
        return self.tokens[i]

    def __repr__(self) -> str:
        tokens_str = ", ".join(map(str, self.tokens))
        return "PART: [{}]".format(tokens_str)

class Lexer:
    def tokenize(self, s: str) -> List:
        result = []

        prev_line_tokens = []
        for i, line in enumerate(s.splitlines()):
            try:
                line_tokens = []
                # Skip empty lines
                if len(line) == 0:
                    continue
                
                # Skip any string with comments
                if line.lstrip().startswith(COMMENTS_STARTER):
                    continue

                # If line begins with Tab, then continue previous line
                if line.startswith(CONTINUE_SYMBOL):
                    line_tokens = prev_line_tokens
                    result.pop(-1) #remove line from previous iteration
                    # In case there was no PARTS_SPLITTER token in the end of previous line
                    if line_tokens[-1] != PARTS_SPLITTER:
                        line_tokens.append(Dot())
                
                parts = line.split(PARTS_SPLITTER)
                for p in parts:
                    if len(p) == 0:
                        continue
                    p_stripped = p.strip()
                    tokens = [Token(x) for x in p_stripped.split(TOKENS_SPLITTER)]
                    part = Part(tokens)
                    line_tokens.append(part)
                    line_tokens.append(Dot())

                result.append(line_tokens)
                prev_line_tokens = line_tokens
            except Exception as e:
                print("Error in lexing line {}: {}".format(i, e))
                raise e

        return result
from typing import List

COMMENTS_STARTER = "--"
CONTINUATION_SYMBOL = "\t"
PARTS_SPLITTER = " . "
TOKENS_SPLITTER = " "

PARTS_SPLITTER_TOKEN = "DOT"

class Token:
    """Base class for tokens
    """ 

    def __init__(self, s: str):
        self.token = s 

    def __repr__(self) -> str:
        return "TOKEN: {}".format(self.token)

    def __call__(self) -> str:
        return self.token

class Dot(Token):
    """Class for "."-token, which is a delimiter between commands
    """

    def __init__(self):
        super().__init__(PARTS_SPLITTER_TOKEN)
    
    def __repr__(self) -> str:
        return PARTS_SPLITTER_TOKEN

class Part:
    """ Class for representing a single command - combination of Tokens
    """

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens

    def __getitem__(self, i) -> str:
        return self.tokens[i]

    def __repr__(self) -> str:
        tokens_str = ", ".join(map(str, self.tokens))
        return "PART: [{}]".format(tokens_str)

class Lexer:
    """ Lexer class.
    It's capable of tokenizing an input string 
    """

    def tokenize(self, s: str) -> List[Part]:
        """Tokenizes an input string and returns a list of tokens.
        During tokenization it removes all empty strings and all comments (see COMMENTS_STARTER constant).
        Line break can be treated as a continuation of the previous command if it starts with a special symbol (see CONTINUATION_SYMBOL constant)

        Args:
            s (str): input string

        Raises:
            e: Any error during lexing

        Returns:
            List[Part]: list, containing `Part` objects (which are list of `Token` objects internaly) separated by `Dot` objects
        """        
        #accumulator of results
        result = []

        #buffer to remember tokens from the previous line in case we encounter continuation after the line break
        prev_line_tokens = []

        #line by line
        for i, line in enumerate(s.splitlines()):
            try:
                line_tokens = []

                # Skip empty lines
                if len(line.strip()) == 0:
                    continue
                
                # Skip any string with comments
                if line.lstrip().startswith(COMMENTS_STARTER):
                    continue

                # If line begins with CONTINUATION_SYMBOL, then continue list of tokens from the previous line
                if line.startswith(CONTINUATION_SYMBOL):
                    line_tokens = prev_line_tokens
                    result.pop(-1) #remove last element from the result because we are continuing it
                    # In case there was no PARTS_SPLITTER token in the end of previous line we add it
                    if line_tokens[-1] != PARTS_SPLITTER:
                        line_tokens.append(Dot())
                
                parts = line.split(PARTS_SPLITTER)
                for p in parts:
                    p_stripped = p.strip()
                    
                    # in case of consecutive PARTS_SPLITTER without any tokens in between we just ignore it
                    if len(p_stripped) == 0:
                        continue

                    # splitting a string between two PARTS_SPLITTER into separate tokens by TOKENS_SPLITTER
                    tokens = [Token(x) for x in p_stripped.split(TOKENS_SPLITTER)]
                    part = Part(tokens) # all tokens between two PARTS_SPLITTER is a single Part
                    line_tokens.append(part)
                    line_tokens.append(Dot()) # adding a Dot as a separator of parts

                result.append(line_tokens) # adding all parts from this line to the results
                prev_line_tokens = line_tokens # remembering this line in case of continuation in the next line
            except Exception as e:
                e.add_note("Error in lexing line: {}".format(line))
                raise

        return result
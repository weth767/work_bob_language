"""
Desenvolvido por: 
Alunos: João Paulo de Souza RA:0035329
        Leandro Souza Pinheiro RA:0015137 

"""
import ply.lex as lex

# Como será indentificado a classe principal ou método principal ?

# Palavras reservadas
reserved_words = {
    "class" : "CLASS",
    "static" : "STATIC",
    "if" : "IF",
    "else" : "ELSE",
    "do" : "DO",
    "for" : "FOR",
    "foreach" : "FOREACH",
    "while" : "WHILE",
    "break" : "BREAK",
    "continue" : "CONTINUE",
    "return" : "RETURN",
    "new" : "NEW",
    "nil" : "NIL",
    "in"  : "IN",
    "def" : "DEF",
    "var" : "VAR",
}

# Tokens
tokens = [
    "ID",
    "INT",
    "FLOAT",
    "STRING",
    "ATRIB",
    "COMMA",
    "SEMICOLON",
    "ARROW",
    "OPENPARENT",
    "CLOSEPARENT",
    "OPENBRACE",
    "CLOSEBRACE",
    "OPENSQUAREBRACKET",
    "CLOSESQUAREBRACKET",
    "COLON",
    "COLONCOLON",
    "NOT",
    "NOTEQUALS",
    "TERNARYIF",
    "MOD",
    "EQUALS",
    "GREATER",
    "GREATEREQUALS",
    "GREATERGREATER",
    "LESS",
    "LESSEQUALS",
    "LESSLESS",
    "BINARYOR",
    "OR",
    "BINARYAND",
    "AND",
    "TILDE",
    "PLUS",
    "MINUS",
    "TIMES",
    "DIV",
    "PLUSPLUS",
    "MINUSMINUS",
    "PLUSEQUALS",
    "MINUSEQUALS",
    "TIMESEQUALS",
    "DIVEQUALS"] + list(reserved_words.values())

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved_words.get(t.value, 'ID')  # Check for reserved words
    return t

def t_FLOAT(t):
    r'\d+(\.\d*)'
    t.value = float(t.value)
    return t

def t_INT(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_STRING(t):
    r'["]([^"\\\n]|\\.|\\\n)*["]'
    t.value = str(t.value)
    return t

# Simbols 
t_ATRIB                 = r'='
t_COMMA                 = r','
t_SEMICOLON             = r';'
t_ARROW                 = r'\->'
t_OPENPARENT            = r'\('
t_CLOSEPARENT           = r'\)'
t_OPENBRACE             = r'\{'
t_CLOSEBRACE            = r'\}'
t_OPENSQUAREBRACKET     = r'\['
t_CLOSESQUAREBRACKET    = r'\]'
t_COLON                 = r':'
t_COLONCOLON            = r'::'

# Logic Operators
t_NOT                   = r'\!'
t_TERNARYIF             = r'\?'
t_EQUALS                = r'=='
t_NOTEQUALS             = r'\!='
t_GREATER               = r'>'
t_GREATEREQUALS         = r'>='
t_GREATERGREATER        = r'>>'
t_LESS                  = r'<'
t_LESSEQUALS            = r'<='
t_LESSLESS              = r'<<'
t_BINARYOR              = r'\|'
t_OR                    = r'\|\|'
t_BINARYAND             = r'&'
t_AND                   = r'&&'
t_TILDE                 = r'~'

# Arithmetic Operators
t_PLUS                  = r'\+'
t_MINUS                 = r'\-'
t_TIMES                 = r'\*'
t_DIV                   = r'/'

t_PLUSPLUS              = r'\+\+'
t_MINUSMINUS            = r'\-\-'
t_PLUSEQUALS            = r'\+='
t_MINUSEQUALS           = r'\-='
t_TIMESEQUALS           = r'\*='
t_DIVEQUALS             = r'/='

# Define uma ExpReg para tratar line numbers
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Define ExpRegs para descartar partes da entrada
t_ignore_SPACES = r'[ \t]+' # espacos brancos
t_ignore_COMMENT = r'\#.*'  # comentarios


# Error handling rule
def t_error(t):
    t.type = 'ERROR'
    t.value = t.value[0]
    t.lexer.skip(1)
    return t

# EOF handling rule
def t_eof(t):
    r''
    return None


lexer = lex.lex()

if __name__ == '__main__':

    filename = 'test.bob'
    file = open(filename, 'r')
    text = file.read()
    lexer.input(text)

    while True:
        tok = lexer.token()
        if tok is None:
            break  # No more input
        print(tok)
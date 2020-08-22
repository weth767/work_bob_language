import ply.yacc as yacc
from scanner import tokens, lexer
from enum import Enum
import logging

class AST(Enum):
    BLOCK = 1
    COMMAND = 2
    EXPRESSION = 3
    COMM_SEQ = 4
    NUMBER = 5
    ID = 6

class NodeAST:
    def __init__(self, type, children=None):
        if not isinstance(type, AST):
            raise ValueError('Tipo nao definido para NodeAST')
        else:
            self.type = type
        if children:
            self.children = children
        else:
            self.children = list()


precedence = ( 
    ('left', 'COMMA'),
    ('right', 'ATRIB', 'PLUSEQUALS', 'MINUSEQUALS', 'TIMESEQUALS', 'DIVEQUALS'),
    ('right', 'TERNARYIF', 'COLON'),
    ('left', 'OR'),
    ('left', 'AND'),
    ('left', 'BINARYOR'),
    ('left', 'BINARYAND'),
    ('left', 'EQUALS', 'NOTEQUALS'),
    ('nonassoc', 'LESS', 'LESSEQUALS', 'GREATEREQUALS', 'GREATER'),
    ('left', 'LESSLESS', 'GREATERGREATER'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIV', 'MOD'),
    ('right', 'UMINUS', 'UPLUS'),
    ('right', 'PLUSPLUS', 'MINUSMINUS', 'NOT', 'TILDE'),
    ('left', 'OPENPARENT', 'CLOSEPARENT', 'OPENSQUAREBRACKET', 'CLOSESQUAREBRACKET', 'ARROW') 
)

def p_Program(p):
    'Program : DefinitionList'
    pass
    """
    p[0] = p[1]
    """

def p_DefinitionList(p):
    """
    DefinitionList : DefinitionList Definition 
                   | empty
    """
    pass
    """
    if (len(p) == 2):
        p[0] = NodeAST(AST.COMM_SEQ, [p[1], p[0]])
    else:
        pass
    """

def p_Definition(p):
    """Definition : ClassDefinition 
                  | FunctionDefinition"""
    pass
    """              
    p[0] = p[1]
    """

def p_ClassDefinition(p):
    'ClassDefinition : CLASS ID OptClassBase OPENBRACE MemberList CLOSEBRACE'
    pass
    """
    id = NodeAST(AST.ID, [p[2]])
    children = ['CLASS', id, p[3], p[5]]
    p[0] = NodeAST(AST.COMM_SEQ, children)
    """

def p_FunctionDefinition(p):
    'FunctionDefinition : DEF OptEnvClass ID OPENPARENT OptParamList CLOSEPARENT Block'
    pass
    """
    id = NodeAST(AST.ID, [p[3]])
    children = ['DEF',p[2], id, p[5], p[7]]
    p[0] = NodeAST(AST.COMM_SEQ, children)
    """

def p_OptClassBase(p):
    """OptClassBase : COLON ID 
                    | empty"""
    pass
    """                
    if (len(p) == 2):
        id = NodeAST(AST.ID, [p[1]])
        children = ["COLON", id]
        p[0] = NodeAST(AST.COMM_SEQ, children)
    else:
        pass
    """

def p_MemberList(p):
    """
    MemberList : MemberList MemberDefinition 
               | empty
    """
    pass
    """
    if (len(p) == 2):
        p[0] = p[1].children + [p[2]]
    else:
        pass
    """

def p_MemberDefinition(p):
    """
    MemberDefinition : OptModifier VAR VariableList SEMICOLON 
                     | OptModifier DEF ID OPENPARENT OptFormArgsList CLOSEPARENT SEMICOLON
    """
    pass
    """
    if (len(p) == 3):
        children = [p[1], "VAR", p[3], "SEMICOLON"]
        p[0] = NodeAST(AST.COMM_SEQ, children)
    else:
        id = NodeAST(AST.ID, [p[3]])
        children = [p[1], "DEF", id, p[5], "SEMICOLON"]
        p[0] = NodeAST(AST.COMM_SEQ, children)
    """


def p_OptModifier(p):
    """
    OptModifier : STATIC 
                | empty
    """
    pass
    """
    if (len(p) == 1):
        p[0] = NodeAST(AST.EXPRESSION)
    else:
        pass
    """

def p_VariableList(p):
    """
    VariableList : VariableList COMMA Variable 
                 | Variable
    """
    pass
    """
    if (len(p) == 3):
        p[0] = p[1].children + [p[3]]
    else:
        p[0] = p[1]
    """

def p_Variable(p):
    """
    Variable : ID 
             | ID OPENSQUAREBRACKET NUMBER CLOSESQUAREBRACKET
    """
    pass
    """
    if (len(p) == 4):
        id = NodeAST(AST.ID, [p[1]])
        number = ''
        if (isinstance(p[3], int)):
            number = str(p[3])
        else:
            number = p[3]
        children = [id, number]
        p[0] = NodeAST(AST.EXPRESSION, children)
    else:
        p[0] = NodeAST(AST.ID)
    """

def p_OptFormArgsList(p):
    """
    OptFormArgsList : FormArgsList 
                    | empty
    """
    pass
    """
    if (len(p) == 1):
        p[0] = p[1]
    else:
        pass
    """

def p_OptEnvClass(p):
    """
    OptEnvClass : ID COLONCOLON 
                | empty
    """
    pass
    """
    if (len(p) == 2):
        p[0] = NodeAST(AST.ID)
    else:
        pass
    """

def p_OptParamList(p):
    'OptParamList : OptFormArgsList OptTempList'
    pass
    """
    children = [p[1],p[2]]
    p[0] = NodeAST(AST.COMM_SEQ, children)
    """

def p_OptTempList(p):
    """
    OptTempList : SEMICOLON FormArgsList 
                | empty
    """
    pass
    """
    if (len(p) == 2):
        p[0] = p[2]
    else:
        pass
    """

def p_FormArgsList(p):
    """
    FormArgsList : FormArgsList COMMA ID 
                 | ID
    """
    pass
    """
    if (len(p) == 3):
        id = NodeAST(AST.ID, [p[3]])
        children = ["COMMA", id]
        p[0] = p[1].children + children
    else:
        p[0] = NodeAST(AST.ID, [p[1]])
    """


def p_Block(p):
    'Block : OPENBRACE CommandList CLOSEBRACE'
    pass
    """
    p[0] = p[2]
    """

def p_CommandList(p):
    """
    CommandList : CommandList Command 
                | empty
    """
    pass

    """
    if (len(p) == 2):
        children = [p[2]]
        p[0] = p[1].children + children
    else:
        pass
    """

def p_Command(p):
    """
    Command : IF OPENPARENT OptExp CLOSEPARENT Command ELSE Command
            | IF OPENPARENT OptExp CLOSEPARENT Command
            | WHILE OPENPARENT OptExp CLOSEPARENT Command
            | DO Command WHILE OPENPARENT OptExp CLOSEPARENT SEMICOLON
            | FOR OPENPARENT OptExp SEMICOLON OptExp SEMICOLON OptExp CLOSEPARENT Command
            | FOREACH ID IN ID Command
            | BREAK SEMICOLON
            | CONTINUE SEMICOLON
            | RETURN OptExp SEMICOLON
            | OptExp SEMICOLON
            | Block
    """
    pass

def p_OptExp(p):
    """
    OptExp : Exp 
           | empty
    """
    pass
    """
    if (len(p) == 1):
        p[0] = p[1]
    else:
        pass
    """

def p_Exp(p):
    """
    Exp : Exp COMMA Exp
        | LeftVal ATRIB Exp
        | LeftVal PLUSEQUALS Exp
        | LeftVal MINUSEQUALS Exp
        | LeftVal TIMESEQUALS Exp
        | LeftVal DIVEQUALS Exp
        | Exp TERNARYIF Exp COLON Exp
        | Exp OR Exp
        | Exp AND Exp
        | Exp BINARYOR Exp
        | Exp BINARYAND Exp
        | Exp LESSLESS Exp
        | Exp GREATERGREATER Exp
        | Exp EQUALS Exp
        | Exp NOTEQUALS Exp
        | Exp GREATEREQUALS Exp
        | Exp LESSEQUALS Exp
        | Exp GREATER Exp
        | Exp LESS Exp
        | Exp PLUS Exp
        | Exp MINUS Exp
        | Exp TIMES Exp
        | Exp DIV Exp
        | Exp MOD Exp
        | MINUSMINUS LeftVal
        | PLUSPLUS LeftVal
        | LeftVal MINUSMINUS
        | LeftVal PLUSPLUS
        | NOT Exp
        | TILDE Exp
        | MINUS Exp %prec UMINUS
        | PLUS Exp %prec UPLUS
        | NEW ID OPENPARENT OptArgs CLOSEPARENT
        | ID OPENPARENT OptArgs CLOSEPARENT
        | Exp ARROW ID OPENPARENT OptArgs CLOSEPARENT
        | ID
        | ID OPENSQUAREBRACKET Exp CLOSESQUAREBRACKET
        | Number
        | STRING
        | NIL
    """
    pass

def p_OptArgs(p):
    """
    OptArgs : Args 
           | empty
    """
    pass
    """
    if (len(p) == 1):
        p[0] = p[1]
    else:
        pass
    """

def p_Args(p):
    """
    Args : Args COMMA Exp 
         | Exp
    """
    pass
    """
    if (len(p) == 3):
        children = [p[1], "COMMA", p[3]]
        p[0] = NodeAST(AST.EXPRESSION, children)
    else:
        p[0] = p[1]
    """

def p_LeftVal(p):
    """
    LeftVal : ID 
            | ID OPENSQUAREBRACKET Exp CLOSESQUAREBRACKET
    """
    pass
    """
    if (len(p) == 1):
        p[0] = NodeAST(AST.ID, [p[1]])
    else:
        children = [NodeAST(AST.ID, [p[1]]), p[3]]
        p[0] = NodeAST(AST.EXPRESSION, children)
    """

def p_Number(p):
    """
    Number : FLOAT 
           | INT 
    """
    pass

def p_empty(p):
    'empty :'
    pass

# Error rule for syntax errors
def p_error(p):
    if p is None:
        print("Syntax error at EOF")
    else:
        print("Syntax error at token", p.type, "line=", p.lineno)

# Build the parser
logging.basicConfig(
     level = logging.DEBUG,
     filename = "parselog.txt",
     filemode = "w",
     format = "%(filename)10s:%(lineno)4d:%(message)s"
)
log = logging.getLogger()
parser = yacc.yacc(debug=True, debuglog=log)

if __name__ == '__main__':
    filename = 'test2.bob'
    file = open(filename, 'r')
    text = file.read()

    result = parser.parse(text, lexer=lexer)
    print(result)

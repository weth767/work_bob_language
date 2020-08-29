"""
Desenvolvido por: 
Alunos: João Paulo de Souza RA:0035329
        Leandro Souza Pinheiro RA:0015137 

"""
import ply.yacc as yacc
from scanner import tokens, lexer, reserved_words
from enum import Enum
import logging

class AST(Enum):
    BLOCK = 1
    COMMAND = 2
    EXPRESSION = 3
    COMM_SEQ = 4
    NUMBER = 5
    STRING = 6
    ID = 7

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
    ('left', 'ARROW') 
)
"""
('left', 'OPENPARENT', 'CLOSEPARENT', 'OPENSQUAREBRACKET', 'CLOSESQUAREBRACKET', 'ARROW') 
"""

def p_Program(p):
    'Program : DefinitionList'
    p[0] = p[1]

def p_DefinitionList(p):
    """
    DefinitionList : DefinitionList Definition 
                   | empty
    """
    if (len(p) == 3):
        p[0] = NodeAST(AST.COMM_SEQ, [p[1], p[0]])
    else:
        pass

def p_Definition(p):
    """Definition : ClassDefinition 
                  | FunctionDefinition"""
    p[0] = p[1]

def p_ClassDefinition(p):
    """
    ClassDefinition : CLASS ID COLON ID OPENBRACE MemberList CLOSEBRACE
                    | CLASS ID OPENBRACE MemberList CLOSEBRACE
    """
    children = None
    if len(p) == 6:
        id = NodeAST(AST.ID, [p[2]])
        children = ['CLASS', id, p[4]]
    else:
        id = NodeAST(AST.ID, [p[2]])
        id2 = NodeAST(AST.ID, [p[4]])
        children = ['CLASS', id, p[3], id2, p[6]]

    p[0] = NodeAST(AST.COMM_SEQ, children)    

def p_FunctionDefinition(p):
    """
    FunctionDefinition : DEF ID COLONCOLON ID OPENPARENT OptParamList CLOSEPARENT Block
                       | DEF ID OPENPARENT OptParamList CLOSEPARENT Block
    """
    children = None
    if len(p) == 7:
        id = NodeAST(AST.ID, [p[2]])
        children = ['DEF', id, p[4], p[6]]
    else:
        id = NodeAST(AST.ID, [p[2]])
        id2 = NodeAST(AST.ID, [p[4]])
        children = ['DEF', id, id2, p[6], p[8]]

    p[0] = NodeAST(AST.COMM_SEQ, children)

def p_MemberList(p):
    """
    MemberList : MemberList MemberDefinition 
               | empty
    """
    pass
    """
    if (len(p) == 3):
        p[0] = p[1].children + [p[2]]
    else:
        pass
    pass
    """

def p_MemberDefinition(p):
    """
    MemberDefinition : OptModifier VAR VariableList SEMICOLON 
                     | OptModifier DEF ID OPENPARENT OptFormArgsList CLOSEPARENT SEMICOLON
    """
    children = None
    if len(p) == 5:
        children = [p[1], "VAR", p[3]]
        p[0] = NodeAST(AST.COMM_SEQ, children)
    else:
        id = NodeAST(AST.ID, [p[3]])
        children = [p[1], "DEF", id, p[5]]
    
    p[0] = NodeAST(AST.COMM_SEQ, children)

def p_OptModifier(p):
    """
    OptModifier : STATIC 
                | empty
    """
    if len(p) == 2:
        p[0] = NodeAST(AST.EXPRESSION, "STATIC")
    else:
        pass

def p_VariableList(p):
    """
    VariableList : VariableList COMMA Variable 
                 | Variable
    """
    if len(p) == 2:
        p[0] = p[1]
    else:
        children = list(p[1].children) + [p[3]]
        p[0] = NodeAST(AST.COMM_SEQ, children)

def p_Variable(p):
    """
    Variable : ID 
             | ID OPENSQUAREBRACKET INT CLOSESQUAREBRACKET
    """
    if len(p) == 2:
        p[0] = NodeAST(AST.ID, p[1])
    else:
        id = NodeAST(AST.ID, [p[1]])
        children = [id, p[3]]
        p[0] = NodeAST(AST.COMM_SEQ, children)

def p_OptFormArgsList(p):
    """
    OptFormArgsList : FormArgsList 
                    | empty
    """
    if len(p) == 2:
        p[0] = p[1]
    else:
        pass

def p_OptParamList(p):
    'OptParamList : OptFormArgsList OptTempList'
    children = [p[1], p[2]]
    p[0] = NodeAST(AST.COMM_SEQ, children)

def p_OptTempList(p):
    """
    OptTempList : SEMICOLON FormArgsList 
                | empty
    """
    if len(p) == 3:
        p[0] = p[2]
    else:
        pass

def p_FormArgsList(p):
    """
    FormArgsList : FormArgsList COMMA ID 
                 | ID
    """
    if len(p) == 2:
        p[0] = NodeAST(AST.ID, p[1])
    else:
        id = NodeAST(AST.ID, p[3])
        children = list(p[1].children) + [id]
        p[0] = NodeAST(AST.COMM_SEQ, children)


def p_Block(p):
    'Block : OPENBRACE CommandList CLOSEBRACE'
    p[0] = p[2]

def p_CommandList(p):
    """
    CommandList : CommandList Command 
                | empty
    """
    pass
    """
    if len(p) == 3:
        children = p[1].children + [p[2]]
        p[0] = NodeAST(AST.COMM_SEQ, children)
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
    if len(p) == 2:
        p[0] = NodeAST(AST.BLOCK, p[1])
    
    elif len(p) == 3:
        if p[1] in reserved_words:
            p[0] = NodeAST(AST.COMMAND, p[1])
        else:
            p[0] = NodeAST(AST.COMM_SEQ, p[1])
    elif len(p) == 6:
        # WHILE OPENPARENT OptExp CLOSEPARENT Command
        # FOREACH ID IN ID Command
        # IF OPENPARENT OptExp CLOSEPARENT Command
        children = None
        if reserved_words[p[1]] == 'foreach':
            id1 = NodeAST(AST.ID, p[2])
            id2 = NodeAST(AST.ID, p[4])
            children = [p[1], id1, id2, p[5]]
        else:
            children = [p[1], p[3], p[5]]
        
        p[0] = NodeAST(AST.COMMAND, children)
    
    elif len(p) == 8:
        children = None
        if reserved_words[p[1]] == 'if':
            # IF OPENPARENT OptExp CLOSEPARENT Command ELSE Command
            children = [p[1], p[3], p[5], p[6], p[7]]
        else:
            # DO Command WHILE OPENPARENT OptExp CLOSEPARENT SEMICOLON
            children = [p[1], p[2], p[3], p[5]]
        p[0] = NodeAST(AST.COMMAND, children)
    
    elif len(p) == 10:
        # FOR OPENPARENT OptExp SEMICOLON OptExp SEMICOLON OptExp CLOSEPARENT Command
        children = [p[1], p[3], p[5], p[7], p[9]]
        p[0] = NodeAST(AST.COMMAND, children)
        
    

def p_OptExp(p):
    """
    OptExp : Exp 
           | empty
    """
    if len(p) == 2:
        p[0] = p[1]
    else:
        pass

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
        | FLOAT
        | INT
        | STRING
        | NIL
        | OPENPARENT Exp CLOSEPARENT
    """
    if len(p) == 2:
        if isinstance(p[1], int):
            children = ['INT', str(p[1])]
            p[0] = NodeAST(AST.NUMBER, children)
        elif isinstance(p[1], float):
            children = ['FLOAT', str(p[1])]
            p[0] = NodeAST(AST.NUMBER, children)
        elif isinstance(p[1], str):
            children = ['STRING', p[1]]
            p[0] = NodeAST(AST.STRING, children)
        else:
            children = None
            if p[1] in reserved_words:
                 children = ['NIL', p[1]]
                 p[0] = NodeAST(AST.EXPRESSION, children)
            else:
                children = ['ID', p[1]]
                p[0] = NodeAST(AST.ID, children)

    elif len(p) == 3:
        children = [p[1], p[2]]
        p[0] = NodeAST(AST.EXPRESSION, children)
    
    elif len(p) == 4:
        if not isinstance(p[1], NodeAST):
        # ( Exp )
            p[0] = p[2]
        else:
            p[0] = NodeAST(AST.EXPRESSION, [p[2], p[1], p[3]])
    
    elif len(p) == 5:
        # ID OPENPARENT OptArgs CLOSEPARENT
        # ID OPENSQUAREBRACKET Exp CLOSESQUAREBRACKET
        id = NodeAST(AST.ID, p[1])
        children = [id, p[3]]
        p[0] = NodeAST(AST.EXPRESSION, children)
    
    elif len(p) == 6:
        # NEW ID OPENPARENT OptArgs CLOSEPARENT
        # Exp TERNARYIF Exp COLON Exp
        if p[1] in reserved_words:
            id = NodeAST(AST.ID, p[2])
            children = ['NEW', id, p[4]]
        else:
            children = [p[2], p[1], p[3], p[5]]

        p[0] = NodeAST(AST.EXPRESSION, children)
    
    elif len(p) == 7:
        # Exp ARROW ID OPENPARENT OptArgs CLOSEPARENT
        id = NodeAST(AST.ID, p[3])
        children = [p[1], p[2], id, p[5]]
        p[0] = NodeAST(AST.EXPRESSION, children)



def p_OptArgs(p):
    """
    OptArgs : Args 
           | empty
    """
    if len(p) == 2:
        p[0] = p[1]
    else:
        pass

def p_Args(p):
    """
    Args : Args COMMA Exp 
         | Exp
    """
    if len(p) == 2:
        p[0] = p[1]
    else:
        children = p[1].children + [p[3]]
        p[0] = NodeAST(AST.COMM_SEQ, children)


def p_LeftVal(p):
    """
    LeftVal : ID 
            | ID OPENSQUAREBRACKET Exp CLOSESQUAREBRACKET
    """
    if len(p) == 2: 
        p[0] = NodeAST(AST.ID, p[1])
    else:
        id = NodeAST(AST.ID, p[1])
        children = [id, p[3]]
        p[0] = NodeAST(AST.COMM_SEQ, children)

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
    filename = 'test.bob'
    file = open(filename, 'r')
    text = file.read()

    result = parser.parse(text, lexer=lexer)
    print(result)

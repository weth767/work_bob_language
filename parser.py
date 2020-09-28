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
    # approaching the command
    ATC = 4
    FLOAT = 5
    INT = 6
    STRING = 7
    ID = 8
    MOD_CLFUN = 9
    VARIABLE = 10

class NodeAST:
    def __init__(self, type, children=None):
        if not isinstance(type, AST):
            raise ValueError('Tipo nao definido para NodeAST')
        else:
            self.type = type
        if children:
            self.children = children
        else:
            self.children = dict()


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
    p[0] = NodeAST(AST.ATC, {'definitionList': p[1]})

def p_DefinitionList(p):
    """
    DefinitionList : DefinitionList Definition 
                   | empty
    """
    if (len(p) == 3):
        p[0] = NodeAST(AST.ATC, {'definitionList': p[1], 'definition': p[2]})
    else:
        pass

def p_Definition(p):
    """Definition : ClassDefinition 
                  | FunctionDefinition"""
    p[0] = NodeAST(AST.ATC, {'cfDefinition': p[1]})
    
def p_ClassDefinition(p):
    """
    ClassDefinition : CLASS ID COLON ID OPENBRACE MemberList CLOSEBRACE
                    | CLASS ID OPENBRACE MemberList CLOSEBRACE
    """
    children = dict()
    if len(p) == 6:
        id = NodeAST(AST.ID,{ 'id': p[2]})
        children = {'class': p[1], 'idClass': id, 'memberList': p[4]}
    else:
        id = NodeAST(AST.ID, {'id': p[2]})
        id2 = NodeAST(AST.ID, {'id': p[4]})
        children = {'class': p[1], 'idClass': id, 'idSuperClass': id2, 'memberList': p[6]}
    p[0] = NodeAST(AST.COMMAND, children)    

def p_FunctionDefinition(p):
    """
    FunctionDefinition : DEF ID COLONCOLON ID OPENPARENT OptParamList CLOSEPARENT Block
                       | DEF ID OPENPARENT OptParamList CLOSEPARENT Block
    """
    children = dict()
    if len(p) == 7:
        id = NodeAST(AST.ID, {'id': p[2]})
        children = {'def': p[1], 'idFunction': id, 'optParamList': p[4], 'block': p[6]}
    else:
        id = NodeAST(AST.ID, {'id': p[2]})
        id2 = NodeAST(AST.ID, {'id': p[4]})
        children = {'def': p[1], 'idFunction': id, 'idClassFunction': id2, 'optParamList': p[6], 'block': p[8]}
    p[0] = NodeAST(AST.COMMAND, children)

def p_MemberList(p):
    """
    MemberList : MemberList MemberDefinition 
               | empty
    """
    children = dict()
    if (len(p) == 3):
        children = {'memberList': p[1], 'memberDefinition': p[2]}
    else:
        children = dict()
    p[0] = NodeAST(AST.ATC, children)

def p_MemberDefinition(p):
    """
    MemberDefinition : OptModifier VAR VariableList SEMICOLON 
                     | OptModifier DEF ID OPENPARENT OptFormArgsList CLOSEPARENT SEMICOLON
    """
    children = dict()
    if len(p) == 5:
        children = {'optModifier': p[1], 'var': p[2], 'variableList': p[3]}
        p[0] = NodeAST(AST.COMMAND, children)
    else:
        id = NodeAST(AST.ID, {'id': p[3]})
        children = {'optModifier': p[1], 'def': p[2], 'memberId': id, 'optFormArgsList': p[5]}
    p[0] = NodeAST(AST.COMMAND, children)

def p_OptModifier(p):
    """
    OptModifier : STATIC 
                | empty
    """
    children = dict()
    if len(p) == 2:
        children = {'static': p[1]}
    p[0] = NodeAST(AST.MOD_CLFUN, children)

def p_VariableList(p):
    """
    VariableList : VariableList COMMA Variable 
                 | Variable
    """
    children = dict()
    if len(p) == 2:
        children = {'variable': p[1]}
    else:
        children = {'variableList': p[1], 'variable': p[3]}
    p[0] = NodeAST(AST.ATC, children)

def p_Variable(p):
    """
    Variable : ID 
             | ID OPENSQUAREBRACKET INT CLOSESQUAREBRACKET
    """
    if len(p) == 2:
        p[0] = NodeAST(AST.ID, {'id': p[1]})
    else:
        id = NodeAST(AST.ID, {'id': p[1]})
        children = {'idVariable': id, 'int': p[3]}
        p[0] = NodeAST(AST.VARIABLE, children)

def p_OptFormArgsList(p):
    """
    OptFormArgsList : FormArgsList 
                    | empty
    """
    if len(p) == 2:
        p[0] = NodeAST(AST.ATC, {'formArgsList': p[1]})
    else:
        pass

def p_OptParamList(p):
    'OptParamList : OptFormArgsList OptTempList'
    children = {'optFormArgsList': p[1], 'optTempList': p[2]}
    p[0] = NodeAST(AST.ATC, children)

def p_OptTempList(p):
    """
    OptTempList : SEMICOLON FormArgsList 
                | empty
    """
    if len(p) == 3:
        p[0] = NodeAST(AST.ATC, {'formArgsList': p[2]})
    else:
        pass

def p_FormArgsList(p):
    """
    FormArgsList : FormArgsList COMMA ID 
                 | ID
    """
    if len(p) == 2:
        id = NodeAST(AST.ID, {'id': p[1]})
        children = {'parameterId': id}
        p[0] = NodeAST(AST.ATC, children)
    else:
        id = NodeAST(AST.ID, {'id': p[3]})
        children = {'formArgsList': p[1], 'parameterId': id}
        p[0] = NodeAST(AST.ATC, children)

def p_Block(p):
    'Block : OPENBRACE CommandList CLOSEBRACE'
    p[0] = NodeAST(AST.ATC, {'commandList': p[2]})

def p_CommandList(p):
    """
    CommandList : CommandList Command 
                | empty
    """
    children = dict()
    if len(p) == 3:
        children = {'commandList': p[1], 'command': p[2]}
    p[0] = NodeAST(AST.ATC, children)   

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
        p[0] = NodeAST(AST.BLOCK, {'block': p[1]})
    elif len(p) == 3:
        # CONTINUE SEMICOLON
        # BREAK SEMICOLON
        # OptExp SEMICOLON
        if p[1] in reserved_words:
            p[0] = NodeAST(AST.COMMAND, {'lCommand': p[1]})
        else:
            p[0] = NodeAST(AST.ATC, {'optExp': p[1]})
    elif len(p) == 6:
        # WHILE OPENPARENT OptExp CLOSEPARENT Command
        # FOREACH ID IN ID Command
        # IF OPENPARENT OptExp CLOSEPARENT Command
        children = dict()
        if reserved_words[p[1]] == 'FOREACH':
            id1 = NodeAST(AST.ID, {'id': p[2]})
            id2 = NodeAST(AST.ID, {'id': p[4]})
            children = {'foreachloop': p[1], 'iterator': id1, 'values' : id2, 'command' : p[5]}
        else:
            name = ''
            if p[1] == 'while':
                name = 'whileLoop'
            else:
                name = 'ifConditional'
            children = {name : p[1], 'optExp': p[3], 'command': p[5]}
        p[0] = NodeAST(AST.COMMAND, children)
    elif len(p) == 8:
        children = dict()
        if reserved_words[p[1]] == 'IF':
            # IF OPENPARENT OptExp CLOSEPARENT Command ELSE Command
            children = {'ifConditional': p[1], 'optExp': p[3], 'command': p[5], 'elseConditional' : p[6],
            'command': p[7]}
        else:
            # DO Command WHILE OPENPARENT OptExp CLOSEPARENT SEMICOLON
            children = {'doLoop': p[1], 'command': p[2], 'whileLoop': p[3], 'optExp' : p[5]}
        p[0] = NodeAST(AST.COMMAND, children)
    elif len(p) == 10:
        # FOR OPENPARENT OptExp SEMICOLON OptExp SEMICOLON OptExp CLOSEPARENT Command
        children = {'forLoop': p[1], 'optExp': p[3], 'optExp': p[5], 'optExp': p[7], 'command': p[9]}
        p[0] = NodeAST(AST.COMMAND, children)
        
def p_OptExp(p):
    """
    OptExp : Exp 
           | empty
    """
    if len(p) == 2:
        p[0] = NodeAST(AST.ATC, {'exp': p[1]})
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
        # | FLOAT
        # | INT
        # | STRING
        # | NIL
        # | ID
        if isinstance(p[1], int):
            children = {'int': str(p[1])}
            p[0] = NodeAST(AST.INT, children)
        elif isinstance(p[1], float):
            children = {'float': str(p[1])}
            p[0] = NodeAST(AST.FLOAT, children)
        else:
            children = dict()
            if p[1] in reserved_words:
                children = {'nil': p[1]}
                p[0] = NodeAST(AST.EXPRESSION, children)
            elif p[1].find("\""):
                children = {'id': p[1]}
                p[0] = NodeAST(AST.ID, children)
            else:
                children = {'string': p[1]}
                p[0] = NodeAST(AST.STRING, children) 
    elif len(p) == 3:
        # | MINUSMINUS LeftVal
        # | PLUSPLUS LeftVal
        # | LeftVal MINUSMINUS
        # | LeftVal PLUSPLUS
        # | NOT Exp
        # | TILDE Exp
        # | MINUS Exp %prec UMINUS
        # | PLUS Exp %prec UPLUS
        children = dict()
        if p[1] == '-':
            children = {'minus': p[1], 'exp': p[2]}
        elif p[1] == '+':
            children = {'plus': p[1], 'exp': p[2]}
        elif p[1] == '!':
            children = {'not': p[1], 'exp': p[2]}
        else:
            children = {'tilde': p[1], 'exp': p[2]}    
        p[0] = NodeAST(AST.EXPRESSION, children)
    elif len(p) == 4:
        # Exp COMMA Exp
        # | Exp OR Exp
        # | Exp AND Exp
        # | Exp BINARYOR Exp
        # | Exp BINARYAND Exp
        # | Exp LESSLESS Exp
        # | Exp GREATERGREATER Exp
        # | Exp EQUALS Exp
        # | Exp NOTEQUALS Exp
        # | Exp GREATEREQUALS Exp
        # | Exp LESSEQUALS Exp
        # | Exp GREATER Exp
        # | Exp LESS Exp
        # | Exp PLUS Exp
        # | Exp MINUS Exp
        # | Exp TIMES Exp
        # | Exp DIV Exp
        # | Exp MOD Exp
        # | LeftVal ATRIB Exp
        # | LeftVal PLUSEQUALS Exp
        # | LeftVal MINUSEQUALS Exp
        # | LeftVal TIMESEQUALS Exp
        # | LeftVal DIVEQUALS Exp
        # | OPENPARENT Exp CLOSEPARENT
        if p[1] == "(":
            p[0] = NodeAST(AST.EXPRESSION, {'(': p[1], 'exp': p[2], ')': p[3]}) 
        else:
            if p[1].__dict__['type'] == AST.ID:
                p[0] = NodeAST(AST.EXPRESSION, {'id': p[1], 'operator': p[2], 'exp': p[3]})
            else:
                p[0] = NodeAST(AST.EXPRESSION, {'exp': p[1], 'operator': p[2], 'exp': p[3]})    
    elif len(p) == 5:
        # ID OPENPARENT OptArgs CLOSEPARENT
        # ID OPENSQUAREBRACKET Exp CLOSESQUAREBRACKET
        id = NodeAST(AST.ID, {'id': p[1]})
        if p[2] == '(':
            children = {'id': id, 'optArgs': p[3]}
        else:
            children = {'id': id, 'exp': p[3]}
        p[0] = NodeAST(AST.EXPRESSION, children)
    
    elif len(p) == 6:
        # NEW ID OPENPARENT OptArgs CLOSEPARENT
        # Exp TERNARYIF Exp COLON Exp
        if p[1] in reserved_words:
            id = NodeAST(AST.ID, {'id': p[2]})
            children = {'new': p[1], 'id': id, 'optArgs': p[4]}
        else:
            children = {'exp': p[1], '?': p[2], 'exp': p[3], 'exp': p[5]}
        p[0] = NodeAST(AST.EXPRESSION, children)
    elif len(p) == 7:
        # Exp ARROW ID OPENPARENT OptArgs CLOSEPARENT
        id = NodeAST(AST.ID, {'id': p[3]})
        children = {'exp': p[1], '->': p[2], 'id': id, 'optArgs': p[5]}
        p[0] = NodeAST(AST.EXPRESSION, children)

def p_OptArgs(p):
    """
    OptArgs : Args 
           | empty
    """
    if len(p) == 2:
        p[0] = NodeAST(AST.ATC, {'args': p[1]})
    else:
        pass

def p_Args(p):
    """
    Args : Args COMMA Exp 
         | Exp
    """
    if len(p) == 2:
        p[0] = NodeAST(AST.ATC, {'exp': p[1]})
    else:
        children = {'args': p[1], 'exp': p[3]}
        p[0] = NodeAST(AST.ATC, children)

def p_LeftVal(p):
    """
    LeftVal : ID 
            | ID OPENSQUAREBRACKET Exp CLOSESQUAREBRACKET
    """
    if len(p) == 2: 
        p[0] = NodeAST(AST.ID, {'id': p[1]})
    else:
        id = NodeAST(AST.ID, {'id': p[1]})
        children = {'id': id, 'Exp': p[3]}
        p[0] = NodeAST(AST.COMMAND, children)

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

def execute(filename):
    file = open(filename, 'r')
    text = file.read()
    return parser.parse(text, lexer=lexer)

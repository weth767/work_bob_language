import ply.yacc as yacc
from lexico import tokens, lexer
from enum import Enum

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
     ('right', 'NOT'),
     ('left', 'AND', 'OR'),
     ('nonassoc', 'EQUALS', 'NOTEQUALS', 'GREATER', 'LESS', 'GREATEREQUALS', 'LESSEQUALS'),  # Nonassociative operators
     ('left', 'PLUS', 'MINUS'),
     ('left', 'TIMES', 'DIV', 'MOD'),
     ('right', 'PLUSPLUS', 'MINUSMINUS'),   # Unary operators (sinalizados com %prec nas regras)
     )


def p_Prog(p):
    'Program: DefinitionList'
    p[0] = p[1]

def p_DefinitionList(p):
    """
    DefinitionList: DefinitionList Definition | empty
    """
    if (len(p) == 2):
        p[0] = p[1].children + [p[2]]
    else:
        pass

def p_Definition(p):
    """
    Definition: ClassDefinition | FunctionDefinition
    """
    p[0] = p[1]

def p_ClassDefinition(p):
    'ClassDefinition: CLASS ID OptClassBase OPENBRACE MemberList CLOSEBRACE'
    ident = NodeAST(AST.ID, [p[2]])
    children = ['CLASS', ident, p[3], p[5]]
    p[0] = NodeAST(AST.COMM_SEQ, children)

def p_FunctionDefinition(p):
    'FunctionDefinition: ClasseEnvolucroOpcional ID OPENPARENT ListaParametrosOpcionais CLOSEPARENT Block'
    ident = NodeAST(AST.ID, [p[2]])
    children = [p[1], ident, p[4], p[6]]
    p[0] = NodeAST(AST.COMM_SEQ, children)

def p_OptClassBase(p):
    """
    OptClassBase: COLON ID | empty'
    """
    if (len(p) == 2):
        ident = NodeAST(AST.ID, [p[1]])
        children = ["COLON", ident]
        p[0] = NodeAST(AST.COMM_SEQ, children)
    else:
        pass

def p_MemberList(p):
    """
    MemberList: MemberList MemberDefinition | empty
    """
    if (len(p) == 2):
        p[0] = p[1].children + [p[2]]
    else:
        pass

def p_MemberDefinition(p):
    """
    MemberDefinition : OptModifier VariableList SEMICOLON 
    | OptModifier ID OPENPARENT OptFormArgsList CLOSEPARENT SEMICOLON
    """
    if (len(p) == 3):
        children = [p[1], p[2], "SEMICOLON"]
        p[0] = NodeAST(AST.COMM_SEQ, children)
    else:
        ident = NodeAST(AST.ID, [p[2]])
        children = [p[1], ident, p[4], "SEMICOLON"]
        p[0] = NodeAST(AST.COMM_SEQ, children)


def p_OptModifier(p):
    """
    ModificadorOpcional : STATIC | empty
    """
    if (len(p) == 1):
        p[0] = NodeAST(AST.COMM_SEQ)
    else:
        pass

def p_VariableList(p):
    """
    VariableList: VariableList COMMA Variable | Variable
    """
    if (len(p) == 3):
        p[0] = p[1].children + ["COMMA", p[3]]
    else:
        p[0] = p[1]

def p_Variable(p):
    """
    Variable: ID | ID OPENSQUAREBRACKET NUMBER CLOSESQUAREBRACKET
    """
    if (len(p) == 4):
        ident = NodeAST(AST.ID, [p[1]])
        number = ''
        if (isinstance(p[3], int)):
            number = str(p[3])
        else:
            number = p[3]
        children = [ident, number]
        p[0] = NodeAST(AST.EXPRESSION, children)
    else:
        p[0] = NodeAST(AST.ID)

def p_OptFormArgsList(p):
    """
    OptFormArgsList: OptArgsList | empty
    """
    if (len(p) == 1):
        p[0] = p[1]
    else:
        pass

def p_OptArgsList(p):
    """
    OptArgsList: OptArgsList COMMA IDENT | IDENT
    """
    if (len(p) == 3):
        ident = NodeAST(AST.ID, [p[3]])
        p[0] = NodeAST(AST.COMM_SEQ, [ident])
    else:
        p[0] = NodeAST(AST.ID)


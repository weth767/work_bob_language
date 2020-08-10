import ply.yacc as yacc
from lexico import tokens, lexer
from enum import Enum

class AST(Enum):
    DEFINITIONLIST = 1 # ListaDefinicoes
    DEFINITION = 2 # Definicao
    CLASSDEFINITION = 3 # DefinicaoClasse
    FUNCTIONDEFINITION = 4 # DefinicaoFuncao
    IDENT = 5 # DefinicaoFuncao
    OPTIONALBASECLASS = 6 # ClasseBaseOpcional
    MEMBERSLIST = 7 # ListaMembros
    MEMBERDEFINITION = 8 # DefinicaoMembro
    OPTIONALMODIFIER = 9 # ModificadorOpcional
    VARIABLELIST = 10 # ListaVariaveis
    VARIABLE = 11 # Variavel
    NUMBER = 12
    OPTFORMALARGSLIST = 13 # ListaArgsFormaisOpcional
    FORMALARGSLIST = 14 # ListaArgsFormais
    OPTENVCLASS = 15 # ClasseEnvolucroOpcional
    OPTPARAMLIST = 16 # ListaParametrosOpcionais
    BLOCK = 17 # Bloco
    OPTTEMPLIST = 18 # ListaTemporariosOpcionais
    COMMANDLIST = 19 # ListaComandos
    COMMAND = 20 # Comando

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

"""
precedence = (
     ('right', 'NOT'),
     ('left', 'AND', 'OR'),
     ('nonassoc', 'EQUAL', 'DIF', 'GT', 'LT', 'GTE', 'LTE'),  # Nonassociative operators
     ('left', 'PLUS', 'MINUS'),
     ('left', 'TIMES', 'DIV', 'MOD'),
     ('right', 'UMINUS', 'UPLUS'),   # Unary operators (sinalizados com %prec nas regras)
     )
"""
def p_Prog(p):
    'Programa: ListaDefinicoes'
    p[0] = p[1]

def p_DefinitionList(p):
    """
    ListaDefinicoes: ListaDefinicoes Definicao | empty
    """
    if (len(p) == 2):
        p[0] = p[1].children + [p[2]]
    else:
        pass

def p_Definition(p):
    """
    Definicao: DefinicaoClasse | DefinicaoFuncao
    """
    p[0] = p[1]

def p_ClassDefinition(p):
    'DefinicaoClasse: class IDENT ClasseBaseOpcional OPENBRACE ListaMembros CLOSEBRACE'
    ident = NodeAST(AST.IDENT, [p[2]])
    children = ['CLASS', ident, p[3], p[5]]
    p[0] = NodeAST(AST.CLASSDEFINITION, children)

def p_FunctionDefinition(p):
    'DefinicaoFuncao: ClasseEnvolucroOpcional IDENT OPENPARENT ListaParametrosOpcionais CLOSEPARENT Bloco'
    ident = NodeAST(AST.IDENT, [p[2]])
    children = [p[1], ident, p[4], p[6]]
    p[0] = NodeAST(AST.FUNCTIONDEFINITION, children)

def p_OptClassBase(p):
    """
    ClasseBaseOpcional: ":" IDENT | empty'
    """
    if (len(p) == 2):
        ident = NodeAST(AST.IDENT, [p[1]])
        children = ["COLON", ident]
        p[0] = NodeAST(AST.OPTIONALBASECLASS, children)
    else:
        pass

def p_MemberList(p):
    """
    ListaMembros: ListaMembros DefinicaoMembro | empty
    """
    if (len(p) == 2):
        p[0] = p[1].children + [p[2]]
    else:
        pass

def p_MemberDefinition(p):
    """
    DefinicaoMembro : ModificadorOpcional ListaVariaveis ";" 
    | ModificadorOpcional IDENT "(" ListaArgsFormaisOpcional ")" ";"
    """
    if (len(p) == 3):
        children = [p[1], p[2], "SEMICOLON"]
        p[0] = NodeAST(AST.MEMBERDEFINITION, children)
    else:
        ident = NodeAST(AST.IDENT, [p[2]])
        children = [p[1], ident, p[4], "SEMICOLON"]
        p[0] = NodeAST(AST.MEMBERDEFINITION, children)



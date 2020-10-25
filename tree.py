from parser import execute, NodeAST, AST

"""
# Desenvolvido por alunos do IFMG Campus Formiga, Curso de Ciência da Computação
# João Paulo de Souza RA: 0035329
# Leandro Souza Pinheiro RA: 0015137

"""

classHierarchy = dict()
functionHierarchy = dict()
classTable = dict()


# método para montar a hierarquia de classe
def walkingForTreeToMountClassHierarchy(tree):
    if tree is None:
        return
    else:
        if isinstance(tree, NodeAST):
            children = tree.__dict__['children']
            for i in children:
                if isinstance(children[i], NodeAST):
                    currentChild = children[i].__dict__
                    if 'class' in currentChild['children'].keys():
                        node = currentChild['children']
                        className = node['idClass'].__dict__['children']['id']
                        superClassName = None
                        if 'idSuperClass' in node.keys():
                            superClassName = node['idSuperClass'].__dict__['children']['id']
                        if superClassName in classHierarchy.keys():
                            classHierarchy[superClassName][1].append(className)
                        classHierarchy[className] = (superClassName, [])
                    walkingForTreeToMountClassHierarchy(children[i])


def walkingForVariableNamesMember(tree, className, isStatic):
    if tree is None:
        return
    else:
        if not isStatic:
            classTable[className][0].append(tree.__dict__['children']['variable'].__dict__['children']['id'])
        else:
            classTable[className][1].append(tree.__dict__['children']['variable'].__dict__['children']['id'])
        if 'variableList' in tree.__dict__['children'].keys():
            if 'variableList' in tree.__dict__['children'].keys():
                walkingForVariableNamesMember(tree.__dict__['children']['variableList'], className, isStatic)


def walkingForVariableMember(tree, className):
    if tree is None:
        return
    else:
        node = tree.__dict__
        children = node['children']
        for i in children:
            if isinstance(children[i], NodeAST):
                if i == "memberDefinition":
                    currentChild = children[i].__dict__['children']
                    if "variableList" in currentChild.keys():
                        isStatic = children[i].__dict__['children']['optModifier'].__dict__['children']['static'] is not None
                        # posicao 0, lista de nomes de vars da classe
                        # posicao 1, lista de nomes de vars de instancia
                        # posicao 2, lista de nomes de funcoes
                        # posicao 3, lista de nomes de funcoes de instancia
                        walkingForVariableNamesMember(children[i].__dict__['children']['variableList'], className, isStatic)
                walkingForVariableMember(children[i], className)


def walkingForFunctionMember(tree, className):
    if tree is None:
        return
    else:
        node = tree.__dict__
        children = node['children']
        for i in children:
            if isinstance(children[i], NodeAST):
                if i == "memberDefinition":
                    currentChild = children[i].__dict__['children']
                    if "memberId" in currentChild.keys():
                        isStatic = children[i].__dict__['children']['optModifier'].__dict__['children']['static'] is not None
                        # posicao 0, lista de nomes de vars da classe
                        # posicao 1, lista de nomes de vars de instancia
                        # posicao 2, lista de nomes de funcoes
                        # posicao 3, lista de nomes de funcoes de instancia
                        if not isStatic:
                            classTable[className][2].append(children[i].__dict__['children']['memberId'].__dict__['children']['id'])
                        else:
                            classTable[className][3].append(children[i].__dict__['children']['memberId'].__dict__['children']['id'])
                walkingForFunctionMember(children[i], className)


# método para montar a tabela de classes
def walkingForTreeToMountClassTable(tree):
    if tree is None:
        return
    else:
        if isinstance(tree, NodeAST):
            children = tree.__dict__['children']
            for i in children:
                if isinstance(children[i], NodeAST):
                    currentChild = children[i].__dict__
                    if 'class' in currentChild['children'].keys():
                        node = currentChild['children']
                        className = node['idClass'].__dict__['children']['id']
                        classTable[className] = ([], [], [], [])
                        walkingForVariableMember(node['memberList'], className)
                        walkingForFunctionMember(node['memberList'], className)
                    walkingForTreeToMountClassTable(children[i])


def walkingForOptArgs(tree, functionName):
    if tree is None:
        return
    else:
        if 'formArgsList' in tree.__dict__['children'].keys():
            node = tree.__dict__['children']['formArgsList']
            if node is not None :
                functionHierarchy[functionName][1].append(node.__dict__['children']['parameterId'].__dict__['children']['id'])
                if 'formArgsList' in node.__dict__['children'].keys() :
                    if 'parameterId' in node.__dict__['children'].keys():
                        functionHierarchy[functionName][1].append(node.__dict__['children']['formArgsList'].__dict__['children']['parameterId'].__dict__['children']['id'])
                    walkingForOptArgs(node.__dict__['children']['formArgsList'], functionName)


def walkingForOptTemps(tree, functionName):
    if tree is None:
        return
    else:
        if "formArgsList" in tree.__dict__['children'].keys():
            node = tree.__dict__['children']['formArgsList']
            if node is not None :
                functionHierarchy[functionName][2].append(node.__dict__['children']['parameterId'].__dict__['children']['id'])
                if 'formArgsList' in node.__dict__['children'].keys() :
                    if 'parameterId' in node.__dict__['children'].keys():
                        functionHierarchy[functionName][2].append(node.__dict__['children']['formArgsList'].__dict__['children']['parameterId'].__dict__['children']['id'])
                    walkingForOptTemps(node.__dict__['children']['formArgsList'], functionName)


def walkingForFunctionParams(tree, functionName):
    if tree is None:
        return
    else:
        if isinstance(tree, NodeAST):
            walkingForOptTemps(tree.__dict__['children']['optTempList'], functionName)
            walkingForOptArgs(tree.__dict__['children']['optFormArgsList'], functionName)


# método para preencher o dicionario de funções
def walkingForTreeToMountFunctionHierarchy(tree):
    if tree is None:
        return
    else:
        if isinstance(tree, NodeAST):
            children = tree.__dict__['children']
            for i in children:
                if isinstance(children[i], NodeAST):
                    currentChild = children[i].__dict__
                    if 'idClassFunction' in currentChild['children'].keys():
                        node = currentChild['children']
                        functionName = node['idClassFunction'].__dict__['children']['id']
                        className = node['idFunction'].__dict__['children']['id']
                        functionHierarchy[functionName] = (className, [], [], node['block'])
                        walkingForFunctionParams(node['optParamList'], functionName)
                    elif 'idFunction' in currentChild['children'].keys():
                        node = currentChild['children']
                        functionName = node['idFunction'].__dict__['children']['id']
                        # posicao 0, nome da classe que pertence ou none
                        # posicao 1, lista dos nomes dos parametros
                        # posicao 2, lista dos nomes das variaveis temporarias
                        # posicao 3, corpo da função(AST)
                        functionHierarchy[functionName] = (None, [], [], node['block'])
                        walkingForFunctionParams(node['optParamList'], functionName)
                    walkingForTreeToMountFunctionHierarchy(children[i])


def genereteDictonaries(executeFile):
    tree = execute(executeFile)
    walkingForTreeToMountClassHierarchy(tree)
    walkingForTreeToMountClassTable(tree)
    walkingForTreeToMountFunctionHierarchy(tree)
    # reverte as listas porque monta ao contrário
    for fun in functionHierarchy:
        function = functionHierarchy[fun]
        function[1].reverse()
        function[2].reverse()
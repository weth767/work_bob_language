from parser import execute, NodeAST, AST

classHierarchy = dict()
functionHierarchy = dict()
classTable = dict()

# método para montar a hierarquia de classe
def walkingByTreeToMountClassHierarchy(tree):
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
                    #print(children[i].__dict__)
                    walkingByTreeToMountClassHierarchy(children[i]) 

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
def walkingByTreeToMountClassTable(tree):
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
                    walkingByTreeToMountClassTable(children[i])

if __name__ == "__main__":
    tree = execute("test4.bob")
    # print(result.__dict__['children'][1].__dict__['children'][4]
    # .__dict__['children'][0].__dict__['children'].__dict__['children'][1].__dict__)
    walkingByTreeToMountClassHierarchy(tree)
    walkingByTreeToMountClassTable(tree)
    print(classTable)
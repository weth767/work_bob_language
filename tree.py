from parser import execute, NodeAST

classHierarchy = dict()
functionHierarchy = dict()
stack = []

# ainda não funcionando
def walkingByTree(tree):
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
                    walkingByTree(children[i])  
                

if __name__ == "__main__":
    tree = execute("test4.bob")
    # print(result.__dict__['children'][1].__dict__['children'][4]
    # .__dict__['children'][0].__dict__['children'].__dict__['children'][1].__dict__)
    walkingByTree(tree)
    print(classHierarchy)
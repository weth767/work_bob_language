from parser import execute
from typing import List

classHieraquy = dict()

# ainda não funcionando
def walkingByTree(tree):
    if (tree is None):
        return
    currentNode = tree
    print(vars(currentNode))
    if type(currentNode) is list:
        print("")
    else:
        currentChildren = currentNode.__dict__['children']
        print("filhos: ", currentChildren[0].__dict__['children'][0].__dict__)
        print("")
        if (currentChildren[0] == "class" or currentChildren[0] == "CLASS"):
            superClass = None
            if len(currentChildren) == 5:
                superClass = currentChildren[3]
            classHieraquy[currentChildren[1]] = [(superClass, [])]
        return walkingByTree(currentChildren[0])

if __name__ == "__main__":
    result = execute("test4.bob")
    # print(result.__dict__['children'][1].__dict__['children'][4]
    # .__dict__['children'][0].__dict__['children'].__dict__['children'][1].__dict__)
    walkingByTree(result)
    #print(classHieraquy)
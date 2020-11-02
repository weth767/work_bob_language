from enum import Enum

from tree import classHierarchy, functionHierarchy, classTable, genereteDictonaries
from parser import NodeAST, AST
from copy import deepcopy

stack = []

class CONSTANTS(Enum):
    MAX_STACK = 10000


class INTERNAL_FUNCTIONS(Enum):
    PRINT = "print"
    SCANF = "scanf"


# dicionário de funções
# posicao 0, nome da classe que pertence ou none
# posicao 1, lista dos nomes dos parametros
# posicao 2, lista dos nomes das variaveis temporarias
# posicao 3, corpo da função(AST)


def start():
    genereteDictonaries("test2.bob")
    mainFunction = functionHierarchy['main']
    interpreter(mainFunction)


def __resolveType(value):
    t = 'string'
    if type(value) == bool:
        t = 'bool'
    elif type(value) == int:
        t = 'int'
    elif type(value) == float:
        t = 'float'
    elif type(value) == list:
        t = str(len(value))
    return t


def __stack_control_add(env):
    if len(stack) >= CONSTANTS.MAX_STACK.value:
        print("stack overflow error")
        exit()
    stack.append(env)


def __stack_control_remove():
    if len(stack) == 1:
        print("stack underflow error")
        exit()
    removeEnv = stack.pop()
    for key in removeEnv:
        if key in stack[-1].keys():
            stack[-1][key] = removeEnv[key]


def resolveNodeCommand(nodeCommand, commandList):
    if nodeCommand is None:
        return
    else:
        if "command" in nodeCommand.keys():
            currentCommand = nodeCommand['command']
            commandList.append(currentCommand)
            if "commandList" in nodeCommand.keys():
                if bool(nodeCommand['commandList'].__dict__):
                    resolveNodeCommand(nodeCommand['commandList'].__dict__['children'], commandList)


# método para resolver as operações no geral
def resolveOperation(operands, operators, types):
    if len(operands) == 1 and len(operators) == 0:
        t = ''
        if type(operands[0]) == bool:
            t = 'bool'
        elif type(operands[0]) == int:
            t = 'int'
        elif type(operands[0]) == float:
            t = 'float'
        else:
            t = 'string'
        return operands[0], t
    if len(operands) == 2 and type(operands[0]) == list:
        value = operands[0][int(operands[1])]
        t = ''
        if type(value) == bool:
            t = 'bool'
        elif type(value) == int:
            t = 'int'
        elif type(value) == float:
            t = 'float'
        else:
            t = 'string'
        return value, t

    while True:
        index = -1
        for i in range(len(operands)):
            if type(operands[i]) == list:
                index = i
                break
        if index != -1:
            value = operands[index][operands[index + 1]]
            t = __resolveType(value)
            types.insert(index, t)
            types.pop(index + 1)
            types.pop(index + 1)
            operands.insert(index, value)
            operands.pop(index + 1)
            operands.pop(index + 1)
        else:
            break

    if ("+" in operands) or ("-" in operands) or ("*" in operands) or ('/' in operands) \
            or ('++' in operands) or ('--' in operands):
        return resolveArithmeticOperation(operands, operators, types)
    else:
        return resolveLogicOperation(operands, operators, types)


# Método para resolver as operações logicas
def resolveLogicOperation(operands, operators, types):
    result = 0
    operators = []
    for i in range(len(operands)):
        if types[i] == "int" or types[i] == "float" or types[i] == "string" or types[i] == "bool":
            operators.append(str(operands[i]))
        else:
            if len(operators) == 1:
                value1 = operators.pop()
                if operands[i] == "!":
                    operands[i] = "not"
                result = str((eval(operands[i] + " " + value1)))
                operators.append(result)
            else:
                value2 = operators.pop()
                value1 = operators.pop()
                if operands[i] == "&&":
                    operands[i] = "and"
                if operands[i] == "||":
                    operands[i] = "or"
                result = str((eval(value1 + " " + operands[i] + " " + value2)))
                operators.append(result)
    return result, 'bool'


# Método para resolver as operações aritmeticas
def resolveArithmeticOperation(operands, operators, types):
    result = 0
    if len(operands) == 2 and ("++" in operands or "--" in operands):
        t = 'int'
        if operands[1] == "++":
            result = int(operands[0]) + 1
        else:
            result = int(operands[0]) - 1
    else:
        operators = []
        t = ''
        if "string" in types:
            for i in range(len(types)):
                if types[i] != "operator":
                    types[i] = "string"
        for i in range(len(operands)):
            if "string" in types:
                t = "string"
                if operands[i] == '+':
                    value2 = operators.pop()
                    value1 = operators.pop()
                    result = str(value1.replace("\"", "")) + str(value2.replace("\"", ""))
                    operators.append(result)
                else:
                    operators.append(str(operands[i]))
            else:
                if types[i] == "int" or types[i] == "float":
                    t = 'int'
                    if types[i] == "float":
                        t = 'float'
                    operators.append(str(operands[i]))
                else:
                    value2 = operators.pop()
                    value1 = operators.pop()
                    result = str((eval(value1 + operands[i] + value2)))
                    operators.append(result)
    return result, t


def resolveFunction(optExp, env: dict):
    currentFunctionId = optExp['id'].__dict__['children']['id']
    args = optExp['optArgs'].__dict__['children']['args']
    if currentFunctionId == INTERNAL_FUNCTIONS.PRINT.value:
        if args is not None:
            operands = []
            operators = []
            types = []
            resolveExp(args.__dict__, operands, operators, types, env)
            result, t = resolveOperation(operands, operators, types)
            print(result)
    elif currentFunctionId == INTERNAL_FUNCTIONS.SCANF.value:
        if args is not None:
            operands = []
            operators = []
            types = []
            argsList = args.__dict__['children']['exp'].__dict__['children']['exp1'].__dict__
            resolveExp(argsList, operands, operators, types, env)
            t = str(operands[0]).replace("\"", "")
            currentId = args.__dict__['children']['exp'].__dict__['children']['exp2'].__dict__['children']['id']
            if isinstance(currentId, NodeAST):
                currentId = currentId.__dict__['children']['id']
                t = str(args.__dict__['children']['exp'].__dict__['children']["exp1"].__dict__['children']['string']).replace("\"", "")
                index = args.__dict__['children']['exp'].__dict__['children']['exp2'].__dict__['children']['exp'].__dict__['children']
                if "id" in index.keys():
                    index = env[index['id']][2]
                else:
                    index = int(index[t])
                env[currentId][1] = "array"
                if t == "int":
                    env[currentId][2][index] = int(input())
                elif t == "float":
                    env[currentId][2][index] = float(input())
                else:
                    env[currentId][2][index] = input()
            else:
                env[currentId][1] = t
                if t == "int":
                    env[currentId][2] = int(input())
                elif t == "float":
                    env[currentId][2] = float(input())
                else:
                    env[currentId][2] = input()
    else:
        function = functionHierarchy[currentFunctionId]
        newEnv = deepcopy(env)
        __stack_control_add(newEnv)
        if isinstance(args, NodeAST):
            argsList = args.__dict__['children']['exp'].__dict__
            operands = []
            operators = []
            types = []
            resolveExp(argsList, operands, operators, types, env)
            while "," in operands : operands.remove(",")
            # pegando as variaveis locais
            for var in function[2]:
                newEnv[var] = ['var', None, None]
            for var in range(len(function[1])):
                f = operands[var]
                t = __resolveType(f)
                # se o tipo for um digito(representando o tamanho do array), então sabemos que é array
                if t.isdigit():
                    newEnv[function[1][var]] = ['array', t, operands[var]]
                else:
                    newEnv[function[1][var]] = ['var', t, operands[var]]
            __stack_control_add(newEnv)
        else:
            for var in function[2]:
                newEnv[var] = ['var', None, None]
        resolveBlock(function[3], stack[-1])
        __stack_control_remove()


# método para resolver a exp opicional ainda não montada
def resolveArray(exp, env):
    if "id" in exp.keys():
        currentId = exp["id"].__dict__['children']['id']
        if "id" in exp['exp'].__dict__['children'].keys():
            sizeArray = env[exp['exp'].__dict__['children']['id']][2]
        else:
            sizeArray = exp['exp'].__dict__['children']['int']
        env[currentId][0] = "array"
        env[currentId][1] = sizeArray
        env[currentId][2] = [None for i in range(int(sizeArray))]
    elif "exp1" in exp.keys() and "exp2" in exp.keys():
        currentId = exp['exp1'].__dict__['children']['id'].__dict__['children']['id']
        operands1 = []
        operators1 = []
        types1 = []
        resolveExp(exp['exp1'].__dict__, operands1, operators1, types1, env)
        operands2 = []
        operators2 = []
        types2 = []
        resolveExp(exp['exp2'].__dict__, operands2, operators2, types2, env)
        value = operands2[0]
        if types2[0] == 'int':
            value = int(value)
        elif types2[0] == 'float':
            value = float(value)
        array = operands1[0]
        index = operands1[1]
        if type(value) == list:
            index2 = operands2[1]
            array[index] = value[index2]
        else:
            array[index] = value
        env[currentId][2] = array
    elif "operator" in exp.keys() and "exp1" in exp.keys():
        operands = []
        operators = []
        types = []
        resolveExp(exp['exp1'].__dict__, operands, operators, types, env)
        value = operands[0]
        currentId = exp['exp1'].__dict__['children']['id']
        if exp['operator'] == "++":
            env[currentId][2] = int(float(value)) + 1
        else:
            env[currentId][2] = int(float(value)) - 1
        env[currentId][1] = "int"


def resolveOptExp(optExp, env: dict):
    # caso tenha só chamado a variável, somente retorna
    if len(optExp.keys()) == 1 and "id" in optExp.keys():
        return
    # caso tenha id e operator
    if "id" in optExp.keys() and "operator" in optExp.keys():
        # se não houver uma ou mais exps, quer dizer que é só atribuição
        if not optExp["exp"].__dict__['type'] == AST.EXPRESSION:
            # pega o id atual
            currentId = optExp["id"].__dict__['children']['id']
            # e atualiza o env
            for key in optExp["exp"].__dict__['children']:
                if optExp["exp"].__dict__['children'][key] in env.keys():
                    var = optExp["exp"].__dict__['children'][key]
                    env[currentId] = [env[var][0], env[var][1], env[var][2]]
                else:
                    env[currentId] = ["var", key, optExp["exp"].__dict__['children'][key]]
        else:
            # caso contrário, busca as exps para retornar o resultado
            operands = []
            operators = []
            types = []
            currentId = optExp["id"].__dict__['children']['id']
            resolveExp(optExp["exp"].__dict__, operands, operators, types, env)
            result, t = resolveOperation(operands, operators, types)
            env[currentId][1] = t
            env[currentId][2] = result
    else:
        if "optArgs" in optExp:
            resolveFunction(optExp, env)
        else:
            resolveArray(optExp, env)


# método para resolver o comando
def resolveExp(exp, operands, operators, types, env):
    if exp is None:
        return
    else:
        currentExp = exp['children']
        if "exp1" in currentExp.keys():
            resolveExp(currentExp['exp1'].__dict__, operands, operators, types, env)
        if "exp2" in currentExp.keys():
            resolveExp(currentExp['exp2'].__dict__, operands, operators, types, env)
        if "id" in currentExp.keys():
            if isinstance(currentExp["id"], NodeAST):
                currentId = currentExp["id"].__dict__["children"]["id"]
            else:
                currentId = currentExp["id"]
            t = env[currentId][1]
            value = env[currentId][2]
            if t == 'int':
                value = int(float(value))
            elif t == 'float':
                value = float(value)
            operands.append(value)
            types.append(t)
        if "exp" in currentExp.keys():
            resolveExp(currentExp['exp'].__dict__, operands, operators, types, env)
        elif "id" not in currentExp.keys() \
                and "exp" not in currentExp.keys() \
                and "exp1" not in currentExp.keys() \
                and "exp2" not in currentExp.keys():
            t = ''
            value = ''
            for key in currentExp:
                t = key
                value = currentExp[t]
            if t == 'int':
                value = int(value)
            elif t == 'float':
                value = float(value)
            operands.append(value)
            types.append(t)
        if exp['type'] == AST.EXPRESSION:
            if "operator" in currentExp:
                operands.append(currentExp['operator'])
                types.append("operator")


def resolveIf(nodeCommand, env):
    optExp = nodeCommand['optExp'].__dict__['children']
    operands = []
    operators = []
    types = []
    resolveExp(optExp['exp'].__dict__, operands, operators, types, env)
    result, t = resolveOperation(operands, operators, types)
    newEnv = deepcopy(env)
    __stack_control_add(newEnv)
    if result == 'True':
        resolveBlock(nodeCommand['commandIf'].__dict__['children']['block'], newEnv)
    elif "commandElse" in nodeCommand:
        resolveBlock(nodeCommand['commandElse'].__dict__['children']['block'], newEnv)
    __stack_control_remove()


def resolveWhile(nodeCommand, env):
    optExp = nodeCommand['optExp'].__dict__['children']
    operands = []
    operators = []
    types = []
    resolveExp(optExp['exp'].__dict__, operands, operators, types, env)
    result, t = resolveOperation(operands, operators, types)
    newEnv = deepcopy(env)
    __stack_control_add(newEnv)
    while result == 'True':
        resolveBlock(nodeCommand['command'].__dict__['children']['block'], stack[-1])
        operands = []
        operators = []
        types = []
        resolveExp(optExp['exp'].__dict__, operands, operators, types, stack[-1])
        result, t = resolveOperation(operands, operators, types)
    __stack_control_remove()


def resolveFor(nodeCommand, env):
    newEnv = deepcopy(env)
    __stack_control_add(newEnv)
    operands1 = []
    operators1 = []
    types1 = []
    # primeira parte do for
    exp1 = nodeCommand['optExp1'].__dict__['children']['exp'].__dict__
    currentId = exp1['children']['id'].__dict__['children']['id']
    resolveExp(exp1['children']['exp'].__dict__, operands1, operators1, types1, stack[-1])
    result1, type1 = resolveOperation(operands1, operators1, types1)
    stack[-1][currentId][2] = result1
    if type(result1) is int:
        stack[-1][currentId][1] = 'int'
    elif type(result1) is float:
        stack[-1][currentId][1] = 'float'
    else:
        stack[-1][currentId][1] = 'string'
    # segunda parte do for
    exp2 = nodeCommand['optExp2'].__dict__['children']['exp'].__dict__
    operands2 = []
    operators2 = []
    types2 = []
    resolveExp(exp2, operands2, operators2, types2, stack[-1])
    result2, type2 = resolveOperation(operands2, operators2, types2)
    # terceira parte do for
    exp3 = nodeCommand['optExp3'].__dict__['children']['exp'].__dict__
    operands3 = []
    operators3 = []
    types3 = []
    if "exp" in exp3['children'].keys():
        exp3 = exp3['children']['exp'].__dict__
    resolveExp(exp3, operands3, operators3, types3, stack[-1])
    result3, type3 = resolveOperation(operands3, operators3, types3)
    while result2 == "True":
        # resolve o bloco dentro do laço
        resolveBlock(nodeCommand['command'].__dict__['children']['block'], stack[-1])
        # itera na variavel
        stack[-1][currentId][2] = result3
        # teste de condições do for
        # segunda parte do for
        exp2 = nodeCommand['optExp2'].__dict__['children']['exp'].__dict__
        operands2 = []
        operators2 = []
        types2 = []
        resolveExp(exp2, operands2, operators2, types2, stack[-1])
        result2, type2 = resolveOperation(operands2, operators2, types2)
        # terceira parte do for
        exp3 = nodeCommand['optExp3'].__dict__['children']['exp'].__dict__
        operands3 = []
        operators3 = []
        types3 = []
        if "exp" in exp3['children'].keys():
            exp3 = exp3['children']['exp'].__dict__
        resolveExp(exp3, operands3, operators3, types3, stack[-1])
        result3, type3 = resolveOperation(operands3, operators3, types3)
    __stack_control_remove()


def resolveForEach(nodeCommand, env):
    newEnv = deepcopy(env)
    varName = nodeCommand['iterator'].__dict__['children']['id']
    values = nodeCommand['values'].__dict__['children']['id']
    __stack_control_add(newEnv)
    for iterator in env[values][2]:
        if type(iterator) == int:
            stack[-1][varName][1] = "int"
        elif type(iterator) == float:
            stack[-1][varName][1] = "float"
        elif type(iterator) is None:
            stack[-1][varName][1] = None
        else:
            stack[-1][varName][1] = "string"
        stack[-1][varName][2] = iterator
        block = nodeCommand['command'].__dict__['children']['block']
        resolveBlock(block, stack[-1])
    __stack_control_remove()


def resolveDoWhileLoop(nodeCommand, env):
    optExp = nodeCommand['optExp'].__dict__['children']
    operands = []
    operators = []
    types = []
    resolveExp(optExp['exp'].__dict__, operands, operators, types, env)
    result, t = resolveOperation(operands, operators, types)
    newEnv = deepcopy(env)
    __stack_control_add(newEnv)
    resolveBlock(nodeCommand['command'].__dict__['children']['block'], stack[-1])
    operands = []
    operators = []
    types = []
    resolveExp(optExp['exp'].__dict__, operands, operators, types, stack[-1])
    result, t = resolveOperation(operands, operators, types)
    while result == 'True':
        resolveBlock(nodeCommand['command'].__dict__['children']['block'], stack[-1])
        operands = []
        operators = []
        types = []
        resolveExp(optExp['exp'].__dict__, operands, operators, types, stack[-1])
        result, t = resolveOperation(operands, operators, types)
    __stack_control_remove()


def resolveCommand(command, env: dict):
    # pega o comando
    if command is None:
        return
    nodeCommand = command.__dict__["children"]
    # verifica qual é o comando
    if "ifConditional" in nodeCommand:
        resolveIf(nodeCommand, env)
    elif "whileLoop" in nodeCommand:
        resolveWhile(nodeCommand, env)
    elif "forLoop" in nodeCommand:
        resolveFor(nodeCommand, env)
    elif "foreachloop" in nodeCommand:
        resolveForEach(nodeCommand, env)
    elif "doLoop" in nodeCommand:
        resolveDoWhileLoop(nodeCommand, env)
    # break, continue e return
    elif "lCommand" in nodeCommand:
        pass
    # caso for optExp, chama o método para resolve-la passando a exp
    elif "optExp" in nodeCommand:
        resolveOptExp(nodeCommand["optExp"].__dict__["children"]["exp"].__dict__['children'], env)


# método para resolver a lista de comandos
def resolveCommandList(commandList: list, env: dict):
    # para cada comando, chama o método para resolver o comando
    for command in commandList:
        resolveCommand(command, env)


# método para resolver o block
def resolveBlock(block: NodeAST, env: dict):
    # pega o node atual com a lista de comandos
    currentCommandNode = block.__dict__['children']['commandList'].__dict__['children']
    # instancia a lista de comandos vazia
    commandList = []
    # e passa node atual para montar a lista de comandos e facilitar a interpretação
    resolveNodeCommand(currentCommandNode, commandList)
    # reverte a lista, já que ela é montada ao contrário
    commandList.reverse()
    # e chama o método para resolver a lista de comandos
    resolveCommandList(commandList, env)


# função para interpretar uma função ou uma classe
def interpreter(functionOrClass):
    env = {}
    # pegando as variaveis locais
    for var in functionOrClass[2]:
        env[var] = ['var', None, None]
    # pegando os parametros da função
    for par in functionOrClass[1]:
        env[par] = ['par', None]
    # preparando o env para as classes

    __stack_control_add(env)
    # resolve o bloco da função
    resolveBlock(functionOrClass[3], stack[-1])


if __name__ == '__main__':
    start()

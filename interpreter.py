from enum import Enum

from tree import classHierarchy, functionHierarchy, classTable, genereteDictonaries
from parser import NodeAST, AST

stack = []

class INTERNAL_FUNCTIONS(Enum):
    PRINT = "print"
    SCANF = "scanf"

# dicionário de funções
# posicao 0, nome da classe que pertence ou none
# posicao 1, lista dos nomes dos parametros
# posicao 2, lista dos nomes das variaveis temporarias
# posicao 3, corpo da função(AST)


def start():
    genereteDictonaries("test.bob")
    mainFunction = functionHierarchy['main']
    interpreter(mainFunction)


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


# Método para resolver uma expressão, preenchendo os operandos e operadores
def resolveExp(exp, operands: list, operators: list, types: list):
    if exp is None:
        return
    else:
        # precisamos caminhar em ordem
        currentExp = exp.__dict__['children']
        if "exp1" in currentExp.keys():
            resolveExp(currentExp['exp1'], operands, operators, types)
        if "exp2" in currentExp.keys():
            resolveExp(currentExp['exp2'], operands, operators, types)
        if exp.__dict__['type'] == AST.EXPRESSION:
            operators.append(currentExp['operator'])
        else:
            type = ""
            for key in currentExp:
                types.append(key)
                type = key
            operands.append(currentExp[type])


# método para resolver as operações no geral
def resolveOperation(operands, operators, types):
    if ("+" in operators) or ("-" in operators) or ("*" in operators) or ('/' in operators):
        return resolveArithmeticOperation(operands, operators, types)
    else:
        return resolveLogicOperation(operands, operators, types)


# Método para resolver as operações logicas
def resolveLogicOperation(operands, operators, types):
    result = 0
    conectiveOperators = []
    logicalOperands = []
    for op in operators:
        if op == "||" or op == "&&" or op == "==" or op == "!=":
            conectiveOperators.append(op)
            operators.remove(op)
    while len(operands) > 1:
        operator = operators[0]
        if operator == '>':
            result = operands[0] > operands[1]
        elif operator == '<':
            result = operands[0] < operands[1]
        elif operator == '>=':
            result = operands[0] >= operands[1]
        elif operator == '<=':
            result = operands[0] <= operands[1]
        else:
            print("Não implementado para o operador: ", operands[0])
            exit()
        operands.pop(0)
        operands.pop(0)
        operators.pop(0)
        logicalOperands.append(result)
    while len(logicalOperands) > 1:
        operator = conectiveOperators[0]
        if operator == '&&':
            result = logicalOperands[0] and logicalOperands[1]
        elif operator == '||':
            result = logicalOperands[0] or logicalOperands[1]
        elif operator == '==':
            result = logicalOperands[0] == logicalOperands[1]
        elif operator == '!=':
            result = logicalOperands[0] != logicalOperands[1]
        logicalOperands.pop(0)
        logicalOperands.pop(0)
        conectiveOperators.pop(0)
        logicalOperands.insert(0, result)
    return result


# Método para resolver as operações aritmeticas
def resolveArithmeticOperation(operands, operators, types):
    result = 0
    while len(operands) > 1:
        operator = operators[0]
        if types[0] == 'int':
            if operator == '+':
                result = int(operands[0]) + int(operands[1])
            elif operator == '-':
                result = int(operands[0]) - int(operands[1])
            elif operator == '*':
                result = int(operands[0]) * int(operands[1])
            else:
                result = int(operands[0]) / int(operands[1])
        elif types[0] == 'float':
            if operator == '+':
                result = float(operands[0]) + float(operands[1])
            elif operator == '-':
                result = float(operands[0]) - float(operands[1])
            elif operator == '*':
                result = float(operands[0]) * float(operands[1])
            else:
                result = float(operands[0]) / float(operands[1])
        else:
            print("entrou aqui")
            if operator == '+':
                result = str(operands[0]) + str(operands[1])
        operands.pop(0)
        operands.pop(0)
        operators.pop(0)
        operands.insert(0, result)
        types.pop(0)
    return result


def resolveFunction(optExp, env: dict):
    currentFunctionId = optExp['id'].__dict__['children']['id']
    args = optExp['optArgs'].__dict__['children']['args']
    #print(args)
    if currentFunctionId == INTERNAL_FUNCTIONS.PRINT.value or currentFunctionId == INTERNAL_FUNCTIONS.SCANF.value:
        if args is not None:
            operands = []
            operators = []
            types = []
            resolveExp(args.__dict__['children']['exp'], operands, operators, types)
            result = resolveOperation(operands, operators, types)
            print(result)


# método para resolver a exp opicional ainda não montada
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
                env[currentId] = ["var", key, optExp["exp"].__dict__['children'][key]]
        else:
            # caso contrário, busca as exps para retornar o resultado
            operands = []
            operators = []
            types = []
            currentId = optExp["id"].__dict__['children']['id']
            resolveExp(optExp["exp"], operands, operators, types)
            result = resolveOperation(operands, operators, types)
            env[currentId][1] = types[0]
            env[currentId][2] = result
    else:
        resolveFunction(optExp, env)


# método para resolver o comando
def resolveCommand(command, env: dict):
    # pega o comando
    nodeCommand = command.__dict__["children"]
    # verifica qual é o comando
    if "ifConditional" in nodeCommand:
        pass
    elif "whileLoop" in nodeCommand:
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
    # resolve o bloco da função
    resolveBlock(functionOrClass[3], env)
    print(env)


if __name__ == '__main__':
    start()

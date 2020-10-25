from tree import classHierarchy, functionHierarchy, classTable, genereteDictonaries
from parser import NodeAST, AST

stack = []

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


def resolveExp(exp, env: dict, operands: list, operators: list, types: dict):
    if exp is None:
        return
    else:
        rightExp = None
        if "exp2" in exp.__dict__['children']:
            nodeExp = exp.__dict__['children']['exp2'].__dict__['children']
            for key in nodeExp:
                rightExp = nodeExp[key]
                types['type'] = key
            rightOpt = exp.__dict__['children']['operator']
            operators.append(rightOpt)
            operands.append(rightExp)
            resolveExp(exp.__dict__['children']['exp1'], env, operands, operators, types)
        else:
            nodeExp = exp.__dict__['children']
            for key in nodeExp:
                operands.append(nodeExp[key])
                types['type'] = key


# Método para resolver as operações
def resolveOperation(operands, operators, types, ident,  env):
    result = 0
    while len(operands) > 1:
        operator = operators[0]
        if types == 'int':
            if operator == '+':
                result = int(operands[0]) + int(operands[1])
            elif operator == '-':
                result = int(operands[0]) - int(operands[1])
            elif operator == '*':
                result = int(operands[0]) * int(operands[1])
            else:
                result = int(operands[0]) / int(operands[1])
        elif types == 'float':
            if operator == '+':
                result = float(operands[0]) + float(operands[1])
            elif operator == '-':
                result = float(operands[0]) - float(operands[1])
            elif operator == '*':
                result = float(operands[0]) * float(operands[1])
            else:
                result = float(operands[0]) / float(operands[1])
        else:
            if operator == '+':
                result = str(operands[0]) + str(operands[1])
        operands.pop(0)
        operands.pop(0)
        operators.pop(0)
        operands.insert(0, result)
    env[ident][1] = types
    env[ident][2] = result


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
            types = {}
            resolveExp(optExp["exp"], env, operands, operators, types)
            operands.reverse()
            operators.reverse()
            ident = optExp['id'].__dict__['children']['id']
            resolveOperation(operands, operators, types['type'], ident, env)


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


if __name__ == '__main__':
    start()

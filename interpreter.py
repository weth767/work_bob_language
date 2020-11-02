"""
# Desenvolvido por alunos do IFMG Campus Formiga, Curso de Ciência da Computação
# João Paulo de Souza RA: 0035329
# Leandro Souza Pinheiro RA: 0015137

"""

from enum import Enum

from tree import classHierarchy, functionHierarchy, classTable, genereteDictonaries
from parser import NodeAST, AST
from copy import deepcopy
import sys


stack = []


# classes auxiliares
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
    # gena os dicionarios que contem as hierarquias
    params = sys.argv
    filename = ""
    if len(params) == 3 and params[1] == "-f":
        filename = params[2]
    else:
        print("O formato correto é python3 interpreter.py -f 'nome_do_arquivo.bob'")
        exit()
    genereteDictonaries(filename)
    # busca a função main
    if "main" not in functionHierarchy.keys():
        print("Método principal não encontrado!")
        exit()
    # busca a função main
    mainFunction = functionHierarchy['main']
    # manda interpretar a partir dela
    interpreter(mainFunction)


# Método auxiliar para checar os tipos de dados
def __resolveType(value):
    t = 'string'
    if type(value) == bool:
        t = 'bool'
    elif type(value) == int:
        t = 'int'
    elif type(value) == float:
        t = 'float'
    # quando for lista não retorna o tipo e sim seu tamanho, já que lista é heterogenea
    elif type(value) == list:
        t = str(len(value))
    return t


# método para adicionar ambientes na pilha de execução
def __stack_control_add(env):
    if len(stack) >= CONSTANTS.MAX_STACK.value:
        print("stack overflow error")
        exit()
    stack.append(env)


# método para remover ambientes da pilha de execução
def __stack_control_remove():
    if len(stack) == 1:
        print("stack underflow error")
        exit()
    removeEnv = stack.pop()
    for key in removeEnv:
        if key in stack[-1].keys():
            stack[-1][key] = removeEnv[key]


# método para resolver o principio de comando
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

    # verificação para arrays contidos nos operands(ocorre em operações com array)
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

    # separa as operações aritmeticas das logicas
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


# método para resolver as funções
def resolveFunction(optExp, env: dict):
    currentFunctionId = optExp['id'].__dict__['children']['id']
    args = optExp['optArgs'].__dict__['children']['args']
    # verifica se são as duas funções reservadas
    if currentFunctionId == INTERNAL_FUNCTIONS.PRINT.value:
        # se for print, pega os argumentos dele e chama o print do python
        if args is not None:
            operands = []
            operators = []
            types = []
            resolveExp(args.__dict__, operands, operators, types, env)
            result, t = resolveOperation(operands, operators, types)
            print(result)
    elif currentFunctionId == INTERNAL_FUNCTIONS.SCANF.value:
        # se for scanf, espera por duas entrada, o tipo de dado e a variavel a receber o valor do input
        if args is not None:
            operands = []
            operators = []
            types = []
            # primeiro pega a lista de argumentos
            argsList = args.__dict__['children']['exp'].__dict__['children']['exp1'].__dict__
            # resolve a expressão dentro dela
            resolveExp(argsList, operands, operators, types, env)
            # pega o tipo passado no parametro
            t = str(operands[0]).replace("\"", "")
            # em seguida pega o id da variavel ou vetor que irá receber o valor do input
            currentId = args.__dict__['children']['exp'].__dict__['children']['exp2'].__dict__['children']['id']
            # se o id for uma instancia de node, quer dizer que ele é um vetor
            if isinstance(currentId, NodeAST):
                currentId = currentId.__dict__['children']['id']
                # pega o tipo do elemento no scanf
                t = str(args.__dict__['children']['exp'].__dict__['children']["exp1"].__dict__['children']['string']).replace("\"", "")
                # pega o index do array
                index = args.__dict__['children']['exp'].__dict__['children']['exp2'].__dict__['children']['exp'].__dict__['children']
                # verifica se o index é uma variável ou um valor estático
                if "id" in index.keys():
                    index = env[index['id']][2]
                else:
                    index = int(index[t])
                # por fim atribui o tipo e valor com a função input do python
                env[currentId][1] = "array"
                if t == "int":
                    env[currentId][2][index] = int(input())
                elif t == "float":
                    env[currentId][2][index] = float(input())
                else:
                    env[currentId][2][index] = input()
            # senão é só uma variável
            else:
                env[currentId][1] = t
                if t == "int":
                    env[currentId][2] = int(input())
                elif t == "float":
                    env[currentId][2] = float(input())
                else:
                    env[currentId][2] = input()
    # ou se é uma função escrita pelo usuário
    else:
        # busca a função na hierarquia
        function = functionHierarchy[currentFunctionId]
        # novo ambiente
        newEnv = deepcopy(env)
        __stack_control_add(newEnv)
        # verifica se os argumentos são NodeAST, no caso de ter parametro
        if isinstance(args, NodeAST):
            # então pega os argumentos os estão os parametro
            argsList = args.__dict__['children']['exp'].__dict__
            operands = []
            operators = []
            types = []
            # resolve eles
            resolveExp(argsList, operands, operators, types, env)
            # remove as virgulas indesejadas
            while "," in operands : operands.remove(",")
            # pegando as variaveis locais
            for var in function[2]:
                newEnv[var] = ['var', None, None]
            # transforma os parametros em variaveis locais da função para ela ter acesso
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
    # se tiver id nas chaves, quer dizer que é declaração do array
    if "id" in exp.keys():
        currentId = exp["id"].__dict__['children']['id']
        if "id" in exp['exp'].__dict__['children'].keys():
            sizeArray = env[exp['exp'].__dict__['children']['id']][2]
        else:
            sizeArray = exp['exp'].__dict__['children']['int']
        env[currentId][0] = "array"
        env[currentId][1] = sizeArray
        env[currentId][2] = [None for i in range(int(sizeArray))]
    # senão é o array recebendo um valor
    elif "exp1" in exp.keys() and "exp2" in exp.keys():
        # resolve ambas as expressões
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
        # converte os tipos de dados do array e variavel
        if types2[0] == 'int':
            value = int(value)
        elif types2[0] == 'float':
            value = float(value)
        array = operands1[0]
        index = operands1[1]
        # se o tipo do valor é igual uma lista, então é um array na posição recebendo outro array em outra posição
        if type(value) == list:
            index2 = operands2[1]
            array[index] = value[index2]
        else:
            # senão é o array recebendo um valor simples ou variavel
            array[index] = value
        # atualiza os dados do array no ambiente
        env[currentId][2] = array
    elif "operator" in exp.keys() and "exp1" in exp.keys():
        # para verificação de ++ e --
        operands = []
        operators = []
        types = []
        # resolve a expressão e verifica qual o tipo deve ser feito
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
            # expressão precisa ser resolvida
            resolveExp(optExp["exp"].__dict__, operands, operators, types, env)
            result, t = resolveOperation(operands, operators, types)
            env[currentId][1] = t
            env[currentId][2] = result
    else:
        # caso não verificou como operações ou atribuição, resolve como função o id
        if "optArgs" in optExp:
            resolveFunction(optExp, env)
        else:
            # senão resolve como array
            resolveArray(optExp, env)


# método para resolver a expressão
def resolveExp(exp, operands, operators, types, env):
    if exp is None:
        return
    else:
        # faz recursão até encontrar os id ou valores simples
        currentExp = exp['children']
        if "exp1" in currentExp.keys():
            resolveExp(currentExp['exp1'].__dict__, operands, operators, types, env)
        if "exp2" in currentExp.keys():
            resolveExp(currentExp['exp2'].__dict__, operands, operators, types, env)
        if "id" in currentExp.keys():
            # quando encontra os ids, busca o valor deles no env atual
            # e também seu tipo e joga na lista de operandos para resolução
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
            # se encontrou os valores simples, faz a mesma coisa que os ids,
            # joga na lista de operandos para resolução
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
            # e por fim verifica qual operação para ser feita
            if "operator" in currentExp:
                operands.append(currentExp['operator'])
                types.append("operator")


# método para resolver os ifs
def resolveIf(nodeCommand, env):
    optExp = nodeCommand['optExp'].__dict__['children']
    operands = []
    operators = []
    types = []
    # resolve a expressão
    resolveExp(optExp['exp'].__dict__, operands, operators, types, env)
    # pega o resultado na resolução lógica
    result, t = resolveOperation(operands, operators, types)
    # empilha o ambiente atual e pega um novo
    newEnv = deepcopy(env)
    __stack_control_add(newEnv)
    # verifica o resultado para saber se vai para o if ou para else, caso exista
    if result == 'True':
        resolveBlock(nodeCommand['commandIf'].__dict__['children']['block'], newEnv)
    elif "commandElse" in nodeCommand:
        resolveBlock(nodeCommand['commandElse'].__dict__['children']['block'], newEnv)
    # depois remove o ambiente da pilha
    __stack_control_remove()


# método para resolver o comando while
def resolveWhile(nodeCommand, env):
    optExp = nodeCommand['optExp'].__dict__['children']
    operands = []
    operators = []
    types = []
    # resolve a expressão
    resolveExp(optExp['exp'].__dict__, operands, operators, types, env)
    # pega o resultado
    result, t = resolveOperation(operands, operators, types)
    # empilha o novo ambiente
    newEnv = deepcopy(env)
    __stack_control_add(newEnv)
    # enquanto o resultado for true, executa o bloco, pegando o novo resultado a cada final de iteração
    while result == 'True':
        resolveBlock(nodeCommand['command'].__dict__['children']['block'], stack[-1])
        operands = []
        operators = []
        types = []
        resolveExp(optExp['exp'].__dict__, operands, operators, types, stack[-1])
        result, t = resolveOperation(operands, operators, types)
    # no fim remove o ambiente atual
    __stack_control_remove()


# método para resolver o laço for
def resolveFor(nodeCommand, env):
    newEnv = deepcopy(env)
    __stack_control_add(newEnv)
    operands1 = []
    operators1 = []
    types1 = []
    # primeira parte do for, onde tem a atribuição inicial
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
    # segunda parte do for, onde faz a comparação se já acabou
    exp2 = nodeCommand['optExp2'].__dict__['children']['exp'].__dict__
    operands2 = []
    operators2 = []
    types2 = []
    resolveExp(exp2, operands2, operators2, types2, stack[-1])
    result2, type2 = resolveOperation(operands2, operators2, types2)
    # terceira parte do for, onde tem o incrimento
    exp3 = nodeCommand['optExp3'].__dict__['children']['exp'].__dict__
    operands3 = []
    operators3 = []
    types3 = []
    if "exp" in exp3['children'].keys():
        exp3 = exp3['children']['exp'].__dict__
    resolveExp(exp3, operands3, operators3, types3, stack[-1])
    result3, type3 = resolveOperation(operands3, operators3, types3)
    # executa o laço até que a condição seja falsa, repetindo os passos 2 e 3
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
    # no final remove o ambiente atual da pilha
    __stack_control_remove()


# método para resolver o laço foreach
def resolveForEach(nodeCommand, env):
    newEnv = deepcopy(env)
    # pega o nome do iterador e dos valores a iterar
    varName = nodeCommand['iterator'].__dict__['children']['id']
    values = nodeCommand['values'].__dict__['children']['id']
    # adiciona o ambiente na pilha
    __stack_control_add(newEnv)
    # realiza o for do python
    for iterator in env[values][2]:
        # atualizando o tipo iterador e pegando o item relacionado a ele
        # para manter o env atualizado
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
        # depois manda executar o bloco de código
        resolveBlock(block, stack[-1])
    # no fim remove o ambiente da pilha
    __stack_control_remove()


# método para resolver o do while
def resolveDoWhileLoop(nodeCommand, env):
    optExp = nodeCommand['optExp'].__dict__['children']
    newEnv = deepcopy(env)
    __stack_control_add(newEnv)
    # resolve o bloco inicial uma vez
    resolveBlock(nodeCommand['command'].__dict__['children']['block'], stack[-1])
    operands = []
    operators = []
    types = []
    # verifica a condição de parada
    resolveExp(optExp['exp'].__dict__, operands, operators, types, stack[-1])
    result, t = resolveOperation(operands, operators, types)
    # se for true, continua resolvendo o bloco
    while result == 'True':
        resolveBlock(nodeCommand['command'].__dict__['children']['block'], stack[-1])
        operands = []
        operators = []
        types = []
        resolveExp(optExp['exp'].__dict__, operands, operators, types, stack[-1])
        result, t = resolveOperation(operands, operators, types)
    # no final remove o ambiente da pihla
    __stack_control_remove()


# método para verificar o comando foi chamado no bob e facilitar a seleção de comandos
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

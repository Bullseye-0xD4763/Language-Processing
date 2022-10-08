import ply.lex as lex
import re
import sys


#Declaração de estruturas de dados
class head:
    def __init__ (self):
        self.nomes = []
    def add(self, string):
        self.nomes.append(string)

class ficheiro:
    def __init__(self):
        self.content = []

    def add(self, string):
        self.content.append(string)


##########################################
#          CONFIGURAÇÃO DO LEX           #
##########################################
tokens = ["CHAVETAE", "CHAVETAD", "PONTO", "FUNC", "NUM", "VIRGULA", "INTER", "BLANK"]
states = [
    ("chaveta", "exclusive"), #state usado para quando pretendemos obter informação dos intervalos
    ("funcao", "exclusive") #state usado para quando pretendemos obter informação  da função utilizada.
]

#Separamos o conteúdo da linha a partir da vírgula. 
def t_VIRGULA(t):
    r'([\w \.@\-\/]+)'
    return t

#São ignoradas as vírgulas dentro das chavetas.
def t_chaveta_VIRGULA(t):
    r','

#Chaveta do lado esquerdo dá início ao contexto "chaveta"
def t_CHAVETAE(t):
    r'{'
    t.lexer.begin("chaveta")

#Chaveta direita fora do contexto "chaveta" é ignorada.
def t_CHAVETAD (t):
    r'}'

#Chaveta direita dentro do contexto "chaveta" marca o fim desse contexto.
def t_chaveta_CHAVETAD(t):
    r'}'
    t.lexer.begin("INITIAL")

# '::' sinaliza uma função
def t_PONTO(t):
    r'::'
    t.lexer.begin("funcao")

#Texto fora do contexto da função é ignorado.
def t_FUNC(t):
    r'\w+'

#Texto dentro do contexto da função é retornado.
def t_funcao_FUNC(t):
    r'\w+'
    t.lexer.begin("INITIAL")
    return t

#Intervalo (analisamos primeiro se é intervalo antes de analisar o número.)
def t_INTER(t):
    r'(\d+,\d+)'

#Números fora do contexto chaveta são ignorados, uma vez que no contexto habitual serão armazenados como strings.
def t_NUM(t):
    r'\d+'

#Intervalo dentro das chavetas
def t_chaveta_INTER(t):
    r'(\d+,\d+)'
    return t
#Números dentro do contexto chaveta são armazenados.
def t_chaveta_NUM(t):
    r'\d+'
    return t

def t_BLANK(t):
    r',,'
    return t
#Funções de erro
def t_error (t):
    t.lexer.skip(1)

def t_chaveta_error(t):
    print("Erro na obtenção de intervalo.")

def t_funcao_error(t):
    print("Erro na obtenção de função.")

#Início do Lex
lexer = lex.lex()
###################################
#       Fim de configuração       #
###################################

###################################
#       Funções Auxiliares        #
###################################

# Vai buscar o segundo argumento de um intervalo. {3,5} -> 5
def intervaloInterpreter(string):
    inter = re.search(r'\d+$', string)
    return inter.group()

# Obtém e guarda o conteúdo do cabeçalho do CSV
def headInterpreter(head):
    k = 0
    lexer.input(head)
    for tok in lexer:
        if tok.type == 'NUM': #Apenas é possível ter o tipo 'NUM' dentro do contexto da chaveta, por isso só procuramos por este tipo.
            groups[k-1] = int(tok.value)
        elif tok.type == 'INTER': #Significa que encontramos o intervalo, processamo-lo com a função intervaloInterpreter()
            res = intervaloInterpreter(tok.value)
            groups[k-1] = int(res)
        elif tok.type == 'FUNC': #Obter o nome da função de agregação que pretendemos obter.
            funcs[k-1] = tok.value
        elif tok.type == 'VIRGULA':
            cabeca.add(tok.value) #Caso não haja nenhum caso excecional, simplesmente armazena a string
            k += 1

# Na situação em que temos um intervalo (i.e. {5}) -> Função cria a lista com os próximos x valores (depende do intervalo e do tamanho total da linha!!)
def listMaker(i, lista):
    isnumero = r'(^[-+]?\d+(\.\d+)?$)'
    isint = r'^(-)?[0-9]+$'
    res = [] #Vamos colocar aqui o resultado final
    for k in range(groups[i]): #Utilizamos o range fornecido pelo header.
        #Verificar sempre que nao excedemos o tamanho da lista. Serve para quando temos situações: 12,13,,, em que na 
        #lista fica como: [12,13]. Assim como não nos interessa de qualquer das formas contar valores "vazios", ignoramos.
        if k+i < len(lista): 
            if re.search(isnumero,lista[k+i]):
                if re.search(isint, lista[k+i]):
                    res.append(int(lista[k+i]))
                else:
                    res.append(float(lista[k+i]))
            k += 1
    return res
           


# Função auxiliar para processar as funções de agregação.
def funcMaker(lista, func):
    #rint = r'^(-)?[0-9]+$'
    if re.search(r'[Ss][Uu][Mm]',func): #caso de termos a função de agregação "sum"
        soma = 0
        for elem in lista:
            soma += elem
        return soma
    if re.search(r'[Mm][Ee][Dd][Ii][Aa]',func): #caso de termos a função de agregação "media"
        soma = 0
        for elem in lista:
            soma += elem
        return soma/len(lista)
    if re.search(r'[Mm][Aa][Xx]',func): #Caso de termos a função de agregação "maior" (extra)
        maximo = -1
        for elem in lista:
            if elem > maximo:
                maximo = elem
        return maximo
    else:
        return []

# Esta função converte uma linha em um dicionário
def converteLine(linha):
    lexer.input(linha)
    temp = []
    dic = {}
    for tok in lexer: #Colocamos todo o conteúdo da linha em uma lista (mais fácil de processar depois...)
        if tok.type == 'VIRGULA':
            temp.append(tok.value)
        elif tok.type == 'BLANK':
            temp.append('')
    i = 0
    k = 0
    while i < (len(temp)):
        if i in funcs: #se estivermos num índice onde ocorre invocação de função.
            nome = "_".join([cabeca.nomes[k], funcs.get(i)]) #Obtemo o novo nome para o campo do dicionário
            aux = listMaker(i,temp)
            dic[nome] = funcMaker(aux, funcs.get(i)) #Primeiro obtemos a lista dos elementos no dado intervalo, depois processamos com a função.
            i += len(aux) #Ajuste... se na listmaker lemos 4 elementos à frente, temos de passar esses 4 elementos à frente
            k += 1
        elif i in groups: #Se estivermos num índice onde ocorre invocação de um interval
            dic[cabeca.nomes[k]] = listMaker(i, temp) #Chamamos a listmaker que retorna a lista com os elementos desse intervalo.
            i += len(dic.get(cabeca.nomes[k]))
            k += 1
        else: #Caso de situação normal (default)
            if not temp[i] == '':
                dic[cabeca.nomes[k]] = temp[i]
                k += 1
            i += 1
    return dic

###################################
#     Fim Funções Auxiliares      #
###################################

###################################
#         Leitura/Escrita         #
###################################

cabeca = head() # Estrutura onde se vai guardar o conteúdo do header da lista.
file = ficheiro() #Estrutura onde se vai guardar o conteúdo do ficheiro (Já com o formato pronto para json -> lista de dicionários)
groups = {} #Dicionário onde vamos guardar os intervalos... key,value -> int, int -> (indice onde ocorre), (valor do intervalo)
funcs = {} #Dicionário onde vamos guardar as invocações de funções... key,value -> int,string->(indice onde ocorre), (nome da função)

#Leitura do ficheiro.
def leitura (nome):
    try:
        f = open(nome,"r")
    except OSError:
        print("Não foi possível aceder ao ficheiro csv.")
        sys.exit()
    with f:
        print("A executar a leitura do ficheiro csv...")
        headInterpreter(next(f)) #Lemos e guardamos informação do header
        texto = f.readlines()
        for linha in texto:
            file.add(converteLine(linha)) #Lemos cada linha, processando-a e armazenando no formato desejado.
        print("Leitura do ficheiro csv terminada.")
        f.close()
    
#Escrita do ficheiro json.
def escrita(nome):    
    print("A escrever o ficheiro json...")
    f = open(nome, "w")
    f.write("[\n")
    k = 0
    for elem in file.content:
        f.write(" " * 4 + "{\n")
        i = 0
        for key, value in elem.items():
            if not type(value) == list and not type(value) == int and not type(value) == float:
                if i < len(elem.items())-1:
                    f.write(" " * 8 + "\"" + str(key) + "\": \"" + str(value) + "\",\n")
                    i += 1
                else:
                    f.write(" " * 8 + "\"" + str(key) + "\": \"" + str(value) + "\"\n")
            else:
                if i < len(elem.items())-1:
                    f.write(" " * 8 + "\"" + str(key) + "\": " + str(value) + ",\n")
                    i += 1
                else:
                    f.write(" " * 8 + "\"" + str(key) + "\": " + str(value) + "\n")
        if k < len(file.content)-1:
            f.write(" " * 4 + "},\n")
        else:
            f.write(" " * 4 + "}\n")
        k += 1
    f.write("]")
    f.close()
    print("Ficheiro json criado com sucesso.")
###################################
#       Fim Leitura/Escrita       #
###################################
#main.. é mais fácil "controlar" a ordem como queremos que tudo execute.
if __name__ == "__main__":
    csv = input('Insira o ficheiro CSV que pretende ler: ')
    while not re.search(r'.csv$', csv):
        csv = input("Certifique-se de que o ficheiro inserido contém a extensão \'.csv\': ")
    json = input('Insira o nome do ficheiro JSON: ')
    while not re.search(r'.json$', json):
        json = input('Certifique-se de que o nome fornecido contém a extensão \'.json\': ')
    leitura(csv)
    escrita(json)
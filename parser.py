import re
import ply.yacc as yacc
import sys

from lexer import tokens

def p_lang(p):
    'lang : LEX comandos YACC regras'
    p[0] = "import ply.lex as l\nimport ply.yacc as yacc\n\n" + str(p[2]) + "lexer = l.lex()\n\n" +str(p[4])    


def p_comandos_empty(p):
    "comandos : "
    p[0] = ""
    

def p_comandos_comando(p):
    "comandos : comando comandos" 
    p[0] = str(p[1]) + str(p[2])
   

def p_comando_literals(p):
    "comando : LITIGN EQ STRING" 
    characters = '"'
    for x in range(len(characters)):
        p[3] = p[3].replace(characters[x],"")
    if p[1] == "%literals":
        final = ""
        i = 0
        for char in p[3]:
            if i != len(p[3])-1:
                final =  final+ "'"+char+"',"
            elif i == len(p[3])-1:
                final =  final+ "'"+char+ "'"
                i += 1
        p[0] = "literals = {"+ final +"}\n"
    elif p[1] == "%ignore":
        p[0] = "t_ignore = \"" + p[3]+ "\"\n"
   


def p_comando_tokens(p):
    "comando : TOKENS EQ LISTA"
    if p[1] == "%tokens":
        if p.parser.reserved == 1:
            p[0] = "tokens = " + p[3]+ " + list(reserved.values())\n\n"
        else :
            p[0] = "tokens = " + p[3]+ "\n\n"
    elif p[1] == "%states":
        p[0] = "states ="+ p[3].replace("'", "\"")+ "\n\n"
#r'\d+(\.\d+)?'   return(´NUMBER´, float(t.value) )
#r'.'   error(f"Illegal character ’{t.value[0]}’, [{t.lexer.lineno}]",t.lexer.skip(1) )
   
# def t_NUMBER(t):
# 	r'\d+(\.\d+)?'
# 	t.value= float(t.value)
# 	return t

# def t_error(t):
# 	r'.'
#   print(f"Illegal character {t.value[0]}, {t.lexer.lineno}")
#   t.lexer.skip(1)


def p_comando_exp(p):
    "comando : EXPRE CODIGO"
    expg = re.findall(r'\'.+\'',p[1])
    s = "'"
    exp = ''.join(char for char in expg[0] if char not in s)
    if "return" in p[2]:
        name = re.findall(r'´.+´',p[2])
        str = "´"
        res = ''.join(char for char in name[0] if char not in str)
        ac = re.findall(r',.+\)',p[2])
        str2 = ","
        r = ''.join(char for char in ac[0] if char not in str2)
        rest = r.replace(' )', '')
        p[0] = "\ndef t_"+res+"(t):\n\tr"+"\""+exp+"\"\n\tt.value =" +rest+"\n\treturn t\n\n"
    else:
        tmp = p[2].split('"')
        q = tmp[1].replace('[{','\'{')
        q2 = q.replace('}]','}\'')
        q3 = q2.replace('\"','')
        acao=""
        i=2
        while i < (len(tmp)):
            tmp[i] = tmp[i].replace(' )', '')
            tmp[i] = tmp[i].replace(',', '')
            acao = "\t"+tmp[i] + "\n"+acao
            i = i+1
        p[0] = "\ndef t_error(t):\n\tr"+"\""+exp+"\"\n\tprint(f\"" + q3 +"\")\n"+acao+"\n"


def p_comando_reseved(p):
    "comando : RESERVED lres FIM"
    p[0] = "reserved = {\n"+p[2]+"}\n"
    p.parser.reserved = 1

def p_lres(p):
    "lres :"
    p[0] = ""

def p_lres_lista(p):
    "lres : res lres"
    if p[2] == "":
        p[0] = p[1] + "\n"
    else:
        p[0] = p[1]+ ",\n" + p[2]

def p_lres_res(p):
    "res : CONT"
    var = p[1].split(":")
    p[0] = "    '"+var[0].strip()+"' : '"+var[1].strip()+"'"
    
def p_comando_id_string(p):
    "comando : ID EQ STRING"
    exp = p[3].replace("\"","'")
    p[0] = p[1]+p[2] + " r"+exp+"\n"
def p_comando_id(p):
    "comando : ID"
    p[0] = p[1]+"\n"

def p_comando_com(p):
    "comando : COMMENT"
    p[0] = p[1] + "\n"


def p_regras_empty(p):
    "regras : "
    p[0]=""
    

def p_regras_regra(p):
    "regras : regra regras"
    p[0] = str(p[1]) + str(p[2])



def p_regra_preced(p):
    "regra : PRECEDENCES EQ LISTA"
    p[0] = "precedence =" + p[3]+ "\n\n"


def p_regra_com(p):
    "regra : COMMENT"
    p[0] = p[1] + "\n"


# y = yacc()     ->         y = yacc.yacc()
# ts = { }
def p_regra_dir(p):
    "regra : ID EQ ID"
    if re.search(r'\d+',p[3]):
        p[0] = p.parser.name +"."+p[1] + p[2] + p[3]+  "\n"
        p.parser.var.append(p[1])
    else:    
        p[0] = p[1] + p[2] + "yacc."+ p[3] + "\n"
        p.parser.name = p[1]

def p_regra_dire(p):
    "regra : ID EQ CODIGO"
    p[0] = p.parser.name +"."+p[1] + p[2] + p[3] + "\n"
    p.parser.var.append(p[1])
   
#y.parse("3+4*7")   ->       y.parse(content)
def p_regra_d(p):
    "regra : ID"
    p[0] = p[1]+"\n"

def p_regra_funcao(p):
    "regra : FUNC CONT"
    ac = p[2]
    i = 0
    while i < len(p.parser.var):
        var = p.parser.var[i]
        name = p.parser.name
        a = ac.replace(var.strip(), name+"."+var.strip())
        ac = a
        i = i + 1
    p[0] = "\n"+p[1]+ "\n    " + a +"\n"

def p_regra_producao(p):
    "regra : PROD lprod FIM"
    p[0] = p[2]

def p_lprod(p):
    "lprod :"
    p[0] = ""

def p_lprod_lista(p):
    "lprod : prod lprod"
    p[0] = p[1] + p[2]


#stat : exp { print(t[1]) } -> def p_2(p):
#                                 "stat : exp"
#                                  print(t[1])
#
#todas as regras têm de ter nomes diferentes
def p_lprod_prod(p):
    "prod : CONT CODIGO"
    s = "}{"
    acao = ''.join(char for char in p[2] if char not in s)
    ac = acao.replace("t[","p[")
    i = 0
    while i < len(p.parser.var):
        var = p.parser.var[i]
        name = p.parser.name
        a = ac.replace(var.strip(), "p."+name+"."+var.strip())
        ac = a
        i = i + 1

    p[0] = "\ndef p_"+ str(p.parser.symcount)+"(p):\n    \""+p[1].strip() +"\"\n    "+ a.strip()+"\n"
    p.parser.symcount += 1

    
def p_error(p):
    print("Syntax error!", p.value)

    

parser = yacc.yacc()
parser.reserved = 0
parser.symcount = 0
parser.name =""
parser.var=[]


try:
    fInput = input("Insert name of the input file:")
    fread = open(fInput, "r")
except OSError:
        print("Não foi possível aceder ao ficheiro.")
        sys.exit()
with fread: 
    fOutput = input("Insert name of the output file:")
    fwrite = open(fOutput, "w")
    content = fread.read()
    fwrite.write(parser.parse(content))
    fwrite.close()

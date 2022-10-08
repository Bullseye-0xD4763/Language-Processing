import re
import ply.lex as l



tokens = ["LEX","YACC",
"LITIGN","TOKENS","PRECEDENCES","RESERVED",
"EXPRE","STRING","COMMENT","LISTA",
"CODIGO", "EQ",
"PROD","ID","FIM","CONT","FUNC"
]

states = [("lang", "inclusive"),
    ("lista", "exclusive"),
    ("regex", "exclusive"),
    ("producao","exclusive"),
    ("funcao","exclusive"),
    ("reserved","exclusive")
]

def t_lang_FUNC(t):
    r'def .+:'
    lexer.push_state("funcao")
    return t

def t_funcao_CONT(t):
    r'(?s)((?:[^\n][\n]?)+)'
    lexer.pop_state()
    return t

def t_lang_PROD(t):
    r'%%P'
    lexer.push_state("producao")
    return t


def t_reserved_CONT(t):
    r'[a-zA-Z]+\s:\s[a-zA-Z]+'
    return t

def t_reserved_FIM(t):
    r"%%F"
    lexer.pop_state()
    return t

def t_producao_CONT(t):
    r'[a-zA-Z]+\s:\s[^{]+'
    return t

def t_producao_CODIGO(t):
    r"\{[^}]+\}"
    return t

def t_producao_FIM(t):
    r"%%F"
    lexer.pop_state()
    return t



def t_lista_EQ(t):
    r'='
    return t

def t_lista_LISTA(t):
    r'\[[^\[\]]+\]'
    lexer.pop_state()
    return t
    
def t_regex_CODIGO(t):
    r'[^\n]+'
    lexer.pop_state()
    return t



def t_lang_EQ(t):
    r'='
    return t

def t_lang_STRING(t):
    r'"[^"]*"'
    return t

def t_lang_LITIGN(t):
    r'(%literals|%ignore)'
    return t




def t_lang_TOKENS(t):
    r'(%tokens|%states)'
    lexer.push_state("lista")
    return t

def t_lang_PRECEDENCES(t):
    r'%precedence'
    lexer.push_state("lista")
    return t

def t_lang_RESERVED(t):
    r'%reserved'
    lexer.push_state("reserved")
    return t

def t_lang_COMMENT(t):
    "(\#)+[^\n]+"
    return t

def t_lang_CODIGO(t):
    "\{.+\}"
    return t


def t_lang_YACC(t):
    r'%%(\s)*YACC'
    return t
   

def t_lang_EXPRE(t):
    r'r\'.+\'(\s)+'
    lexer.push_state("regex")
    return t

#INITIAL

def t_LEX(t):
    r'%%(\s)*LEX'
    lexer.push_state("lang")
    return t

def t_lang_ID(t):
    "[a-z_\(\)\.\"0-9\+\-\*A-Z]+(\s)*"
    return t

#ignore
t_lista_ignore = " "
t_regex_ignore = " \n\t"
t_lang_ignore = " \n\t"
t_producao_ignore = " \n"
t_reserved_ignore = " \n\t"
t_funcao_ignore = " \n"

#error

def t_ANY_error(t):
    print("Illegal character: ", t.value[0])


lexer = l.lex()

#Para teste do lexer
# f = open("/home/sofia/Música/PL/tp2/t3.txt", 'r')
# content = f.read()

# result = lexer.input(content)
# for tok in lexer:
#     print(tok)

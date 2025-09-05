#------------------------------------------------------------------------------------------------------#                      
                    #-----Funções para formatação de nomes-----#
#------------------------------------------------------------------------------------------------------#  

#Função que formata os nomes para deixar padronizdo com as iniciais maiúsculas#
def formatar_nome(nome):
    particulas = {"da", "das", "de", "do", "dos", "e"}
    # Aplica title() pra capitalizar
    nome_formatado = nome.title()
    
    # Quebrar o nome em palavras para avaliar as partículas
    palavras = nome_formatado.split()
    
    # Ajustar partículas para minúsculo
    resultado = []
    for palavra in palavras:
        if palavra.lower() in particulas:
            resultado.append(palavra.lower())
        else:
            resultado.append(palavra)
    
    return " ".join(resultado)
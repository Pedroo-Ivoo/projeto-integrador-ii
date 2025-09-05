import re
import smtplib #biblioteca necesária para o envio de e-mail
from email.mime.text import MIMEText #Biblioteca para usar no e-mail
from email.mime.multipart import MIMEMultipart #Biblioteca para usar no e-mail
import os


#--------------------------------------------------------------------------------------------------------#
                    #---------Funções para verificação de e-mail---------#
#--------------------------------------------------------------------------------------------------------#


#Função que verifica se o e-mail foi escrito dentro do padrão correto#
def verifica_email(email):
    #Expressão regular para verificação da escrita correta de e-mail.
    # "exemplo" + @ + "email" . "com" e ou ."br"
    padrao = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"

    if re.fullmatch(padrao, email):
        return True
    else:
        return False
    
#--------------------------------------------------------------------------------------------------------#
                    #---------Função para envio de e-mail---------#
#--------------------------------------------------------------------------------------------------------#
#Função que envia e-mail para a confirmar cadastro ou refazer a senha
def enviar_email(email, html, assunto):
    #Configurações
    port = os.getenv("port")
    smtp_server = os.getenv("smtp_server")
    login = os.getenv("login")  # Seu login gerado pelo Mailtrap
    password = os.getenv('password')  # Sua senha gerada pelo Mailtrap

    sender_email = os.getenv("sender_email")
    receiver_email = email
    # Conteúdo de email
    subject = assunto
    

    # Criar uma mensagem multipart e definir cabeçalhos
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject

    # Anexar a parte em HTML
    message.attach(MIMEText(html, "html"))

    # Enviar o email
    with smtplib.SMTP(smtp_server, port) as server:
        server.starttls()
        server.login(login, password)
        server.sendmail(sender_email, receiver_email, message.as_string())

    print('Enviado')
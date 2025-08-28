# O arquivo __init__.py transforma a pasta 'models' em um pacote Python.
# Ele centraliza a importação de modelos (tabelas de banco de dados),
# permitindo que eles sejam importados de forma mais limpa em outros arquivos.
# Ex: 'from models import Usuarios'
from .usuarios import Usuarios
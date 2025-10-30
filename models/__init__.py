# O arquivo __init__.py transforma a pasta 'models' em um pacote Python.
# Ele centraliza a importação de modelos (tabelas de banco de dados),
# permitindo que eles sejam importados de forma mais limpa em outros arquivos.
# Ex: 'from models import Usuarios'
from .usuarios import Usuarios
from .regioes import Regioes
from .pais import Pais
from .motoristas import Motoristas
from .alunos import Alunos
from .veiculos import Veiculos
from .alocacao_viagens import AlocacaoViagens
from .alocacaoAlunos import AlocacaoAlunos
from .funcionarios import Funcionario
from .registros import RegistroPonto
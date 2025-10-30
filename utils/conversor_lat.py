# Função que faz  a conversão de endereços em coordenadas latitude e longitude e vice-versa
import googlemaps
from config import gmaps


# Exemplo de função de Geocodificação
def geocodificar_endereco(endereco_completo):
    """
    Converte um endereço de texto em coordenadas geográficas (lat, lng).
    Retorna uma tupla (latitude, longitude) ou (None, None) em caso de falha.
    """
    if not gmaps:
        return None, None # Retorna falha se o cliente não foi inicializado

    try:
        # Tenta geocodificar o endereço
        geocode_result = gmaps.geocode(endereco_completo)
        
        if geocode_result:
            # Pega as coordenadas do primeiro resultado
            localizacao = geocode_result[0]['geometry']['location']
            latitude = localizacao['lat']
            longitude = localizacao['lng']
            return latitude, longitude
        
        # Endereço não encontrado pelo Google
        return None, None
        
    except googlemaps.exceptions.ApiError as e:
        # Lidar com erros específicos da API (ex: KEY_INVALID, OVER_QUERY_LIMIT)
        print(f"Erro na API de Geocodificação: {e}")
        return None, None
    except Exception as e:
        # Erro geral (conexão, etc.)
        print(f"Erro inesperado na Geocodificação: {e}")
        return None, None


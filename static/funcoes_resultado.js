
// Use as variáveis globais definidas no HTML.
// O nome que você injetou no HTML é DADOS_DA_ROTA, vamos usá-lo:
const ESCOLA_COORDENADAS = { lat: -22.176439315824982, lng: -49.96360257116418 };
var dadosDaRota = window.DADOS_DA_ROTA || {}; // Acessa a variável global e usa {} se for undefined

// Verifica se a rota foi calculada (só acontece no POST/redirect)
if (Object.keys(dadosDaRota).length === 0 || !dadosDaRota.polyline_para_desenhar_no_mapa) {
    // Se não houver dados, não faz nada ou mostra uma mensagem
    console.log("Aguardando o cálculo da rota ou rota não encontrada.");
    // Retorna para evitar erros no resto do script
} else {
    // VARIÁVEIS IMPORTANTES, AGORA ACESSADAS CORRETAMENTE:
    var polyline = dadosDaRota.polyline_para_desenhar_no_mapa;
    var ordemOtimizada = dadosDaRota.ordem_otimizada_indices;
    var paradasOriginais = dadosDaRota.paradas_originais;

    function initMap() {
        // 1. INSTANCIA O MAPA NO ELEMENTO HTML 'map'
        const map = new google.maps.Map(document.getElementById("map"), {
            zoom: 12,
            center: ESCOLA_COORDENADAS,
        });
        // 2. Desenhar a rota no mapa
        // A polylinha só será desenhada se 'polyline' existir
        const routePath = new google.maps.Polyline({
            path: google.maps.geometry.encoding.decodePath(polyline),
            // ...
        });
        routePath.setMap(map);

        // Exibir a Distância e Duração (Se os elementos existirem na página)
        if (document.getElementById('distancia')) {
            document.getElementById('distancia').innerText = dadosDaRota.distancia_total_km + ' km';
        }
        if (document.getElementById('duracao')) {
            document.getElementById('duracao').innerText = dadosDaRota.duracao_total_minutos + ' minutos';
        }
    }

    // Função para carregar o Google Maps de forma assíncrona
    function loadScript() {
    if (!document.getElementById('google-maps-script')) {
        var script = document.createElement('script');
        script.id = 'google-maps-script';
        
        // CORREÇÃO: Adicionando 'libraries=geometry' ao script.src
script.src = 'https://maps.googleapis.com/maps/api/js?key=' + API_KEY + '&libraries=geometry&callback=initMap&loading=async';        
        script.defer = true;
        document.head.appendChild(script);
    }
}

    // Chama o carregamento do script
    window.onload = loadScript;
}
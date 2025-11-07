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
    // NOVA VARIÁVEL
    var listaParadasCompleta = dadosDaRota.lista_paradas_completa;


    // Função para adicionar os marcadores (pins) no mapa
    function adicionarMarcadoresNoMapa(map) {
        if (!listaParadasCompleta || listaParadasCompleta.length === 0) {
            console.warn("Lista de paradas não encontrada ou vazia.");
            return;
        }

        listaParadasCompleta.forEach(function(parada) {
            // Converte a string de coordenadas "lat,lng" para um objeto {lat: ..., lng: ...}
            const coords = parada.coordenadas.split(',').map(c => parseFloat(c));
            const position = { lat: coords[0], lng: coords[1] };
            
            // Define o conteúdo do balão de informação (InfoWindow)
            let content = `<strong>${parada.numero_parada}. ${parada.tipo}</strong>`;
            
            if (parada.nome_aluno) {
                content += `<br>Aluno: ${parada.nome_aluno} ${parada.sobrenome_aluno}`;
                content += `<br>Endereço: ${parada.endereco}`;
            } else if (parada.detalhes) {
                content += `<br>${parada.detalhes}`;
            }
            
            // O rótulo do marcador será o número da parada
            // Se for a primeira (0) ou a última parada (Escola), não mostra o rótulo numérico.
            let labelText = parada.numero_parada > 0 && parada.numero_parada < listaParadasCompleta.length - 1 
                            ? parada.numero_parada.toString() 
                            : '';

            // Define um ícone diferente para a escola (início e fim)
            let iconConfig = null;
            if (parada.tipo.includes("Escola")) {
                 iconConfig = {
                    url: 'http://maps.google.com/mapfiles/ms/icons/blue-dot.png', // Ícone azul para a escola
                    scaledSize: new google.maps.Size(32, 32)
                };
            }


            // Cria o marcador
            const marker = new google.maps.Marker({
                position: position,
                map: map,
                title: content.replace(/<br>/g, ' - '), // Título para hover
                label: labelText,
                icon: iconConfig 
            });

            // Adiciona o InfoWindow (o balão que aparece ao clicar)
            const infoWindow = new google.maps.InfoWindow({
                content: content,
            });

            // Adiciona um evento para mostrar o InfoWindow ao clicar
            marker.addListener("click", () => {
                infoWindow.open({
                    anchor: marker,
                    map,
                });
            });
        });
    }


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
            strokeColor: "#000000", // Cor da linha (preto)
            strokeOpacity: 0.8,
            strokeWeight: 4
        });
        routePath.setMap(map);

        // NOVO PASSO: Adicionar os marcadores (pins) no mapa
        adicionarMarcadoresNoMapa(map);


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
        
        // Adicionando 'libraries=geometry' ao script.src
        script.src = 'https://maps.googleapis.com/maps/api/js?key=' + API_KEY + '&libraries=geometry&callback=initMap&loading=async';        
        script.defer = true;
        document.head.appendChild(script);
    }
}

    // Chama o carregamento do script
    window.onload = loadScript;
}
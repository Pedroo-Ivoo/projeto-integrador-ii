$(document).ready(function() {
    // --- Funções de Máscara ---
    function mascaraDoAnoFabricacao(){
        $('#ano_fabricacao').inputmask('9999');
    }
    mascaraDoAnoFabricacao();

    function mascaraPlaca() {
        $('#placa').inputmask('AAA-9*99');
    }
    mascaraPlaca();

    // --- Função de Erro ---
    function msgErro(mensagem){
        $("#msg-error").html('<div class="alert alert-danger" role="alert"><i class="fas fa-exclamation-triangle"></i>' + mensagem + '</div>'); 
    }

    // --- Lógica de Vagas ---
    const tipoSelecionado = document.getElementById('tipo');
    const vagasSelecionada = document.getElementById('vagas');
    
    // ATENÇÃO: Se estiver usando o campo 'vagas' para EDIÇÃO,
    // o valor atual deve ser injetado via Jinja2 aqui (fora do JS, no HTML),
    // ou você pode passá-lo para o JS. Vou simular a obtenção do valor
    // atual do banco de dados (que precisa ser preenchido no seu HTML via Jinja2)
    
   
    const vagasAtuais = document.getElementById('vagas_atuais') ? 
                        document.getElementById('vagas_atuais').value : 
                        null;

    const vagasPorTipo = {
        'Van': [ 12, 15, 18],
        'Micro-ônibus': [15, 20, 25],
        'Ônibus': [25, 30, 40]
    };
    
    // Função para carregar e pré-selecionar as vagas
    function carregarVagas() {
        const tipo = tipoSelecionado.value;
        
        // Limpa e adiciona a opção "Selecione"
        vagasSelecionada.innerHTML = '<option value="">Selecione</option>'; 
        
        if (vagasPorTipo[tipo]) {
            vagasPorTipo[tipo].forEach(function (v) {
                const option = document.createElement('option');
                option.value = v;
                option.textContent = v + " vagas";
                
                // PRÉ-SELEÇÃO DA VAGA
                // Converte 'v' para String para comparação segura
                if (vagasAtuais && String(v) === vagasAtuais) { 
                    option.selected = true; 
                }
                
                vagasSelecionada.appendChild(option)
            })
        }
    }
    
    // 1. CHAMA NO CARREGAMENTO (Resolve o problema de edição)
    carregarVagas(); 

    // 2. CHAMA NO EVENTO CHANGE (Comportamento normal)
    tipoSelecionado.addEventListener('change', carregarVagas);


    // --- Função de Submit e Validação ---
    $('#form').on('submit', function(event){
        event.preventDefault();
        
        // Verifica se a placa foi digitada
        if($('#placa').val().length == 0){
            msgErro('Favor preencher o campo placa');
            return false;
        }
        // Verifica se a modelo foi digitada
        if($('#modelo').val().length == 0){
            msgErro('Favor preencher o campo modelo');
            return false;
        }
        // Verifica se a ano de fabricação foi digitada
        if($('#ano_fabricacao').val().length == 0){
            msgErro('Favor preencher o campo Data de Fabricação');
            return false;
        }
        // Verifica se o tipo foi selecionado
        if($('#tipo').val() == ""){
            msgErro('Favor selecione o tipo de veículo');
            return false;
        }
        // Verifica se a vaga foi selecionado
        if($('#vagas').val() == ""){
            msgErro('Favor selecione o número de vagas');
            return false;
        }
        
        //Validar os dados do input
        const placa = $('#placa').val().trim().toUpperCase().replace(/[^a-zA-Z0-9]/g, '');
        const modelo = $('#modelo').val().trim();
        const ano_fabricacao = $('#ano_fabricacao').val().trim();
        const tipo = $('#tipo').val().trim();
        const vagas = $('#vagas').val().trim();

        //Criar um objeto com os dados do formulário
        const data = {
            placa: placa,
            modelo: modelo,
            ano_fabricacao: ano_fabricacao, 
            tipo: tipo,
            vagas: vagas,
        };
        
        // Envia os dados para o servidor usando fetch API
        fetch(`/${veiculoId}/editar_veiculo`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(result => {
            const container = document.getElementById('msg-feedback');
            container.innerHTML = ''; // Limpa mensagens anteriores

            if (result.erros) {
                result.erros.forEach(msg => {
                    container.innerHTML += `<div class="alert alert-danger">${msg}</div>`;
                });
            } else if (result.mensagem) {
                container.innerHTML = `<div class="alert alert-success">${result.mensagem}</div>`;

                // Limpa o formulário
                document.getElementById('form').reset();

                setTimeout(() => {
                    container.innerHTML = ''; 
                }, 10000);
            } else if (result.erro) {
                container.innerHTML = `<div class="alert alert-danger">Erro inesperado: ${result.erro}</div>`;
            }
        })
        .catch(error => {
            document.getElementById('msg-feedback').innerHTML =
                `<div class="alert alert-danger">Erro de conexão: ${error}</div>`;
        });
    })
})
$(document).ready(function() {
   function mascaraDoAnoFabricacao(){
        $('#ano_fabricacao').inputmask('9999');
    }
    mascaraDoAnoFabricacao();

    function mascaraPlaca() {
    $('#placa').inputmask('AAA-9*99');
}
mascaraPlaca();
    // Função que retorna o erro ao usuário
    function msgErro(mensagem){
        $("#msg-error").html('<div class="alert alert-danger" role="alert"><i class="fas fa-exclamation-triangle"></i>' + mensagem + '</div>'); 
    }

     //Seletor de escolha das vagas dos veículos de acordo com o seu modelo.
                const tipoSelecionado = document.getElementById('tipo');
                const vagasSelecionada = document.getElementById('vagas');

                const vagasPorTipo = {
                    'Van': [ 12,15,18],
                    'Micro-ônibus': [15,20,25],
                    'Ônibus': [25, 30, 40]
                };
                tipoSelecionado.addEventListener('change', function(){
                    const tipo = this.value;
                    vagasSelecionada.innerHTML ='<option value="">Selecione</option>';
                    if (vagasPorTipo[tipo]){
                        vagasPorTipo[tipo].forEach(function (v){
                            const option = document.createElement('option');
                            option.value= v;
                            option.textContent = v + " vagas";
                            vagasSelecionada.appendChild(option)
                        })
                    }
                })


    //Função para validar os campos do formulário
    $('#form').on('submit', function(event){
                console.log("Função de submit acionada!");
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
                console.log(data)
                // Envia os dados para o servidor usando fetch API
                fetch('/cadastro_veiculos', {
                method: 'POST',
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
                                container.innerHTML = ''; // Limpa mensagens anteriores
                // Redireciona para a página inicial após 10 segundos
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

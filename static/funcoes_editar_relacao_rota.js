$(document).ready(function() {
   
    // Função que retorna o erro ao usuário
    function msgErro(mensagem){
        $("#msg-error").html('<div class="alert alert-danger" role="alert"><i class="fas fa-exclamation-triangle"></i>' + mensagem + '</div>'); 
    }

   

    //Função para validar os campos do formulário
    $('#form').on('submit', function(event){
                console.log("Função de submit acionada!");
                event.preventDefault();
            
                // Verifica se o tipo foi selecionado
                if($('#motorista').val() == ""){
                    msgErro('Favor selecione o transporte');
                    return false;
                }
                // Verifica se a vaga foi selecionado
                if ($('input[name="alunos"]:checked').length === 0) {
                    msgErro('É preciso selecionar ao menos um aluno.');
                    return false;
                }
                
                

                //Validar os dados do input
                
                const motorista = $('#motorista').val();
                const alunos = $('input[name="alunos"]:checked').map(function() {
                return this.value;}).get();


                //Criar um objeto com os dados do formulário
                const data = {
                    motorista: motorista,
                    alunos: alunos,
                };
                console.log(data)
                
                // Envia os dados para o servidor usando fetch API
                fetch('/relacao_editar_rotas', {
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

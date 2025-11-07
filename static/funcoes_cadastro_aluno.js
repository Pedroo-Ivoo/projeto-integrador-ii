$(document).ready(function() {
   
    // Função que retorna o erro ao usuário
    function msgErro(mensagem){
        $("#msg-error").html('<div class="alert alert-danger" role="alert"><i class="fas fa-exclamation-triangle"></i>' + mensagem + '</div>'); 
    }


    //Função para validar os campos do formulário
    $('#form').on('submit', function(event){
                event.preventDefault();
                
                // Verifica se a nome foi digitada
                if($('#nome').val().length == 0){
                    msgErro('Favor preencher o campo nome');
                    return false;
                }
                // Verifica se a sobrenome foi digitada
                if($('#sobrenome').val().length == 0){
                    msgErro('Favor preencher o campo sobrenome');
                    return false;
                }
                

                //Validar os dados do input
                const nome = $('#nome').val().trim();
                const sobrenome = $('#sobrenome').val().trim();
                const id_responsavel = $('#responsavel').val().trim();



                //Criar um objeto com os dados do formulário
                const data = {
                    nome: nome,
                    sobrenome: sobrenome,
                    id_responsavel: id_responsavel 

                };
                // Envia os dados para o servidor usando fetch API
                fetch('/cadastro_alunos', {
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

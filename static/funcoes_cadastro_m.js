$(document).ready(function() {
    function mascaraDoTelefone(){
        $('#telefone').inputmask('(99) 99999-9999');
    }
    mascaraDoTelefone();

    // Função que retorna o erro ao usuário
    function msgErro(mensagem){
        $("#msg-error").html('<div class="alert alert-danger" role="alert"><i class="fas fa-exclamation-triangle"></i>' + mensagem + '</div>'); 
    }


    //Função para validar os campos do formulário
    $('#form').on('submit', function(event){
                console.log("Função de submit acionada!");
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
                // Verifica se a email foi digitada
                if($('#email').val().length == 0){
                    msgErro('Favor preencher o campo email');
                    return false;
                }
                // Verifica se a telefone foi digitada
                if($('#telefone').val().length == 0){
                    msgErro('Favor preencher o campo telefone');
                    return false;
                }
                if ($('#regiao').val() == "") {
                    msgErro('Favor selecionar a região da rota');
                    return false;
                }

                //Validar os dados do input
                const nome = $('#nome').val().trim();
                const sobrenome = $('#sobrenome').val().trim();
                const email = $('#email').val().trim();
                const telefone = $('#telefone').val().trim();
                const regiao = $('#regiao').val().trim();

                const data = {
                    nome: nome,
                    sobrenome: sobrenome,
                    email: email,
                    telefone: telefone,
                    regiao: regiao
                };
                // Envia os dados para o servidor usando fetch API
                fetch('/cadastro_motoristas', {
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

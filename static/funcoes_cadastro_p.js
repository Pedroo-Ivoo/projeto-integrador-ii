$(document).ready(function() {
    // Função do input mask para o telefone
    function mascaraDoTelefone(){
        $('#telefone').inputmask('(99) 99999-9999');
    }
    mascaraDoTelefone();

    function mascaraDoCep(){
        $('#cep').inputmask('99999-999');
            } 
    mascaraDoCep();
        
    function limpa_formulário_cep() {
                // Limpa valores do formulário de cep.
                $("#cep").val("");
                $("#rua").val("");
                $("#bairro").val("");
                $("#cidade").val("");
                $("#estado").val("");                
            }

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
                const telefone = $('#telefone').val().trim().replace(/\D/g, '');
                const regiao = $('#regiao').val().trim();
                const cep = $('#cep').val().trim().replace(/\D/g, '');
                const rua = $('#rua').val().trim();
                const numero = $('#numero').val().trim();
                const complemento = $('#complemento').val().trim();
                const bairro = $('#bairro').val().trim();
                const cidade = $('#cidade').val().trim();
                const estado = $('#estado').val().trim();


                //Criar um objeto com os dados do formulário
                const data = {
                    nome: nome,
                    sobrenome: sobrenome,
                    email: email,
                    telefone: telefone,
                    regiao: regiao,
                    cep: cep,
                    rua: rua,
                    numero: numero,
                    complemento: complemento,
                    bairro: bairro,
                    cidade: cidade,
                    estado: estado
                };
                // Envia os dados para o servidor usando fetch API
                fetch('/cadastro_pais', {
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

    //Quando o campo cep perde o foco.
            $("#cep").blur(function() {

                //Nova variável "cep" somente com dígitos.
                var cep = $(this).val().replace(/\D/g, '');

                //Verifica se campo cep possui valor informado.
                if (cep != "") {

                    //Expressão regular para validar o CEP.
                    var validacep = /^[0-9]{8}$/;

                    //Valida o formato do CEP.
                    if(validacep.test(cep)) {

                        //Preenche os campos com "..." enquanto consulta webservice.
                        $("#rua").val("...");
                        $("#bairro").val("...");
                        $("#cidade").val("...");
                        $("#estado").val("...");

                        //Consulta o webservice viacep.com.br/
                        $.getJSON("https://viacep.com.br/ws/"+ cep +"/json/?callback=?", function(dados) {

                            if (!("erro" in dados)) {
                                //Atualiza os campos com os valores da consulta.
                                $("#rua").val(dados.logradouro);
                                $("#bairro").val(dados.bairro);
                                $("#cidade").val(dados.localidade);
                                $("#estado").val(dados.uf);
                            } //end if.
                            else {
                                //CEP pesquisado não foi encontrado.
                                limpa_formulário_cep();
                                alert("CEP não encontrado.");
                            }
                        });
                    } //end if.
                    else {
                        //cep é inválido.
                        limpa_formulário_cep();
                        alert("Formato de CEP inválido.");
                    }
                } //end if.
                else {
                    //cep sem valor, limpa formulário.
                    limpa_formulário_cep();
                }
            });
})

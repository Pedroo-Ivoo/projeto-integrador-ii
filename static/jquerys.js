$(document).ready(function() {

            function limpa_formulário_cep() {
                // Limpa valores do formulário de cep.
                $("#rua").val("");
                $("#bairro").val("");
                $("#cidade").val("");
                $("#estado").val("");                
            }
            // Função do input mask para o preenchimento do campo do cep
            function mascaraDoCep(){
               $('#cep').inputmask('99999-999');
            } 
            mascaraDoCep();
            // Função que retorna o erro ao usuário
            function msgErro(mensagem){
                $("#msg-error").html('<div class="alert alert-danger" role="alert"><i class="fas fa-exclamation-triangle"></i>' + mensagem + '</div>'); 
            }
    
            // Função é chamada quando houver o evento do submit
            $('#form').on('submit', function(event){
                console.log("Função de submit acionada!");
                event.preventDefault();
                
                // Verifica se a senha foi digitada
                if($('#senha').val().length == 0){
                    msgErro('Favor preencher o campo senha');
                    return false;
                }
                    
                // Aqui verifica se o tamanho digitado esta entre 4 e 12
                if($('#senha').val().length < 6 || $('#senha').val().length > 12){
                    msgErro('Sua senha deve ter entre 6 e 12 caracteres!');
                    return false;
                }
                this.submit();
            });

            // Função chamada quando estiver preenchendo o campo senha. Assim ajuda o usuário na sua experiência.
            $('#senha').on('input', function() {
            const senha = $(this).val();
            const regex = /^[\S]{6,12}$/;
            // Quando o input estiver em branco após uma tentativa de escrita ele volta ficar sem destaque de cor
            if (senha === "") {
            $(this).removeClass('is-valid is-invalid');
            return;}

            // Verificador se ao preencher o input preenche os requisitos ou não.
            if (regex.test(senha)) {
                $(this).removeClass('is-invalid').addClass('is-valid');
            } else {
                $(this).removeClass('is-valid').addClass('is-invalid');
            }
            });
            // Função chamada quando estiver preenchendo o campo do usuário.
            $("#usuario").on("input",function(){
            const usuario = $(this).val();
            const regex =/^[a-zA-Z]{3,12}$/;

            if (usuario === "") {
            $(this).removeClass('is-valid is-invalid');
            return;}


            if (regex.test(usuario)) {
                $(this).removeClass('is-invalid').addClass('is-valid');
            } else {
                $(this).removeClass('is-valid').addClass('is-invalid');
            }

});


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
        });


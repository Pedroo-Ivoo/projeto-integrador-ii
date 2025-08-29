       
function mostrarSenha(){
    let inputSenha = document.getElementById("senha");
    let btnExibeSenha = document.getElementById("btn-senha");

    if(inputSenha.type === 'password'){
        inputSenha.setAttribute("type", "text");
        btnExibeSenha.classList.replace("bi-eye", "bi-eye-slash");
    } else{
        inputSenha.setAttribute("type","password")
        btnExibeSenha.classList.replace("bi-eye-slash", "bi-eye");
    }
}

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

            //Função para validar a escolha da opção
            $('#opcao').on('change', function () {
            const valorSelecionado = $(this).val();

            if (valorSelecionado === "Motorista" || valorSelecionado === "Pais") {
             $(this).removeClass('is-invalid').addClass('is-valid');
            } else {
            $(this).removeClass('is-valid').addClass('is-invalid');
             }
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

            // Metodo que valida a confirmação de correspondecencia entre as senhas
            $('#confirmaSenha').on('input', function() {
            const senha = $('#senha').val();
            const confirmaSenha = $(this).val();
            const feedback = $('.feedback-senha');

            if (confirmaSenha === "") {
                $(this).removeClass('is-valid is-invalid');
                feedback.text('');
                return;
            }

            if (confirmaSenha === senha) {
                $(this).removeClass('is-invalid').addClass('is-valid');
                feedback.removeClass('text-danger').addClass('text-success').text('Senhas correspondem');

            } else {
                $(this).removeClass('is-valid').addClass('is-invalid');
                feedback.removeClass('text-success').addClass('text-danger').text('As senhas não coincidem');

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
// Variaveis que controlam o accordion
const accordionCollapseElementList = document.querySelectorAll('#myAccordion .collapse')
const accordionCollapseList = [...accordionCollapseElementList].map(accordionCollapseEl => new bootstrap.Collapse(accordionCollapseEl))
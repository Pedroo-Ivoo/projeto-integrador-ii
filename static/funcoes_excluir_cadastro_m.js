let paiIdSelecionado = null;

function abrirModalExclusao(id) {
  paiIdSelecionado = id;
  const modal = new bootstrap.Modal(document.getElementById('modalConfirmacao'));
  modal.show();
}

document.getElementById('btnConfirmarExclusao').addEventListener('click', function () {
  if (!paiIdSelecionado) return;

  fetch(`/${paiIdSelecionado}/excluir_motorista`, {
    method: 'DELETE',
    headers: { 'Content-Type': 'application/json' }
  })
    .then(response => {
      // 1. Verifica se a resposta HTTP é de sucesso (status 200-299)
      if (response.ok) {
        // Se OK (sucesso), processa o JSON normalmente
        return response.json();
      }

      // 2. Se for um erro HTTP (e.g., 403, 404, 500), processa o corpo como JSON
      // O decorador garante que a resposta 403 é JSON.
      return response.json().then(errorData => {
        // Lança um erro com a mensagem de erro que veio do Python
        // Ex: errorData = {"erro": "Acesso negado..."}
        throw new Error(errorData.erro || `Erro de servidor: Status ${response.status}`);
      });
    })
    .then(result => {
      // Se chegou aqui, a resposta foi 200 OK e JSON
      if (result.mensagem) {
        alert(result.mensagem);
        location.reload();
      } else if (result.erro) {
        // Embora improvável após a verificação de 'response.ok', mantém a segurança
        alert("Erro: " + result.erro);
      }
    })
    .catch(error => {
      // 3. Captura qualquer erro lançado (rede ou o erro do servidor que lançamos no passo 2)
      // Exibe a mensagem de erro específica.
      alert("Erro na operação: " + error.message);
      
      // Opcional: Fechar o modal em caso de erro.
      const modal = bootstrap.Modal.getInstance(document.getElementById('modalConfirmacao'));
      if (modal) {
          modal.hide();
      }
    });
});
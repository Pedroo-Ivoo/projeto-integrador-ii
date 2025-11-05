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
    .then(response => response.json())
    .then(result => {
      if (result.mensagem) {
        alert(result.mensagem);
        location.reload();
      } else if (result.erro) {
        alert("Erro: " + result.erro);
      }
    })
    .catch(error => {
      alert("Erro de conexão: " + error);
    });
});

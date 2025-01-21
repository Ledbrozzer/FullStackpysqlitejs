/* static/script.js */

function openSidebar() {
    document.querySelector(".sidebar").style.width = "250px";
}

function closeSidebar() {
    document.querySelector(".sidebar").style.width = "0";
}

function openModal(modalId) {
    document.getElementById(modalId).style.display = "block";
}

function closeModal(modalId) {
    document.getElementById(modalId).style.display = "none";
}

function confirmarAlteracaoSenha() {
    const novaSenha = document.getElementById('novaSenha').value;
    
    fetch('/alterar_senha', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
            'novaSenha': novaSenha
        }),
    })
    .then(response => {
        if (response.ok) {
            return response.text();
        }
        throw new Error("Erro ao alterar a senha");
    })
    .then(text => {
        alert(text);
        closeModal('alterarSenhaModal');
    })
    .catch(error => {
        console.error('Erro:', error);
        alert('Erro ao alterar a senha');
    });
}

function confirmarAlteracaoNome() {
    const novoNome = document.getElementById('novoNome').value;
    
    fetch('/alterar_nome', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
            'novoNome': novoNome
        }),
    })
    .then(response => {
        if (response.ok) {
            return response.text();
        }
        throw new Error("Erro ao alterar o nome");
    })
    .then(text => {
        alert(text);
        closeModal('alterarNomeModal');
        location.reload();  // Atualiza a página para refletir o novo nome
    })
    .catch(error => {
        console.error('Erro:', error);
        alert('Erro ao alterar o nome');
    });
}

function confirmarCadastroUsuario() {
    const novoUsername = document.getElementById('novoUsername').value;
    const novaSenhaCadastro = document.getElementById('novaSenhaCadastro').value;

    fetch('/cadastrar_usuario', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
            'username': novoUsername,
            'password': novaSenhaCadastro
        }),
    })
    .then(response => {
        if (response.ok) {
            return response.text();
        }
        throw new Error("Erro ao cadastrar o usuário");
    })
    .then(text => {
        alert(text);
        closeModal('cadastrarUsuarioModal');
    })
    .catch(error => {
        console.error('Erro:', error);
        alert('Erro ao cadastrar o usuário');
    });
}

function logout() {
    fetch('/logout').then(() => {
        alert("Você fez logout com sucesso.");
        window.location.href = "/login";
    }).catch(error => {
        console.error('Erro:', error);
        alert('Erro ao fazer logout');
    });
}

function confirmarDelecaoConta() {
    fetch('/deletar_conta', {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
    })
    .then(response => {
        if (response.ok) {
            return response.text();
        }
        throw new Error("Erro ao deletar a conta");
    })
    .then(text => {
        alert(text);
        window.location.href = "/login";  // Redirecionar para a página de login após a deleção da conta
    })
    .catch(error => {
        console.error('Erro:', error);
        alert('Erro ao deletar a conta');
    });
}
async function buscarHistoricoVeiculo() {
    const placa = document.getElementById('historicoVeiculoPlaca').value;
    const mes = document.getElementById('historicoVeiculoMes').value;
    const ano = document.getElementById('historicoVeiculoAno').value;

    if (!placa || !mes || !ano) {
        alert("Por favor, preencha todos os campos: placa, mês e ano.");
        return;
    }

    try {
        const response = await fetch(`/historico_veiculo?placa=${placa}&mes=${mes}&ano=${ano}`);
        if (response.ok) {
            const data = await response.json();
            const resultadoDiv = document.getElementById('resultadoHistorico');
            resultadoDiv.innerHTML = data.map(registro => `
                <p>
                    Placa: ${registro.placa}, Veículo: ${registro.veiculo_equip},
                    Data: ${registro.data_req},
                    Km Atual: ${registro.km_atual}, Litros: ${registro.litros},
                    Diferença de Km: ${registro.diferenca_de_km},
                    Litros Anterior: ${registro.litros_anterior},
                    Km por Litro: ${registro.km_por_litro}
                </p>
            `).join('');
        } else {
            throw new Error("Erro ao buscar histórico do veículo");
        }
    } catch (error) {
        console.error('Erro:', error);
        alert('Erro ao buscar histórico do veículo');
    }
}

async function buscarAbastecimento() {
    const placa = document.getElementById('procurarAbastecimentoPlaca').value;
    const mes = document.getElementById('procurarAbastecimentoMes').value;
    const ano = document.getElementById('procurarAbastecimentoAno').value;

    if (!placa || !mes || !ano) {
        alert("Por favor, preencha todos os campos: placa, mês e ano.");
        return;
    }

    try {
        const response = await fetch(`/procurar_abastecimento?placa=${placa}&mes=${mes}&ano=${ano}`);
        if (response.ok) {
            const data = await response.json();
            const resultadoDiv = document.getElementById('resultadoAbastecimento');
            resultadoDiv.innerHTML = data.map(registro => `
                <div>
                    <p>
                        Placa: ${registro.placa}, Veículo: ${registro.veiculo_equip},
                        Data: ${registro.data_req}, Requisitante: ${registro.requisitante},
                        Km Atual: ${registro.km_atual}, Litros: ${registro.litros},
                        Diferença de Km: ${registro.diferenca_de_km}, Litros Anterior: ${registro.litros_anterior},
                        Km por Litro: ${registro.km_por_litro}
                    </p>
                    <button onclick="selecionarAbastecimento(${registro.id})">Selecionar</button>
                </div>
            `).join('');
        } else {
            throw new Error("Erro ao procurar abastecimento");
        }
    } catch (error) {
        console.error('Erro:', error);
        alert('Erro ao procurar abastecimento');
    }
}

async function deletarAbastecimento(id) {
    const confirmacao = confirm("Tem certeza que deseja deletar este abastecimento?");
    if (!confirmacao) {
        return;
    }

    try {
        const response = await fetch(`/deletar_abastecimento/${id}`, {
            method: 'DELETE',
        });

        if (response.ok) {
            alert("Abastecimento deletado com sucesso");
            location.reload(); // Atualiza a página para refletir as alterações
        } else {
            throw new Error("Erro ao deletar o abastecimento");
        }
    } catch (error) {
        console.error('Erro:', error);
        alert('Erro ao deletar o abastecimento');
    }
}

async function selecionarAbastecimento(id) {
    try {
        const response = await fetch(`/abastecimento/${id}`);
        if (response.ok) {
            const registro = await response.json();
            const resultadoDiv = document.getElementById('resultadoAbastecimento');
            resultadoDiv.innerHTML = `
                <div id="registroSelecionado">
                    <h4>Registro Selecionado</h4>
                    <p>
                        Placa: ${registro.placa}, Veículo: ${registro.veiculo_equip},
                        Data: ${registro.data_req}, Requisitante: ${registro.requisitante},
                        Km Atual: ${registro.km_atual}, Litros: ${registro.litros},
                        Diferença de Km: ${registro.diferenca_de_km}, Litros Anterior: ${registro.litros_anterior},
                        Km por Litro: ${registro.km_por_litro}
                    </p>
                    <button onclick="alterarAbastecimento(${registro.id})">Alterar</button>
                    <button onclick="procurarAbastecimentoAnterior(${registro.id})">Procurar Abastecimento Anterior</button>
                    <button onclick="deletarAbastecimento(${registro.id})">Deletar</button>
                </div>
                <div id="registroAnterior"></div>
            `;
        } else {
            throw new Error("Erro ao buscar detalhes do abastecimento");
        }
    } catch (error) {
        console.error('Erro:', error);
        alert('Erro ao buscar detalhes do abastecimento');
    }
}

async function procurarAbastecimentoAnterior(id) {
    try {
        const response = await fetch(`/abastecimento_anterior/${id}`);
        if (response.ok) {
            const data = await response.json();
            const resultadoDiv = document.getElementById('registroAnterior');
            resultadoDiv.innerHTML = `
                <h4>Abastecimento Anterior</h4>
                <p>
                    Placa: ${data.placa}, Veículo: ${data.veiculo_equip},
                    Data: ${data.data_req}, Requisitante: ${data.requisitante},
                    Km Atual: ${data.km_atual}, Litros: ${data.litros},
                    Diferença de Km: ${data.diferenca_de_km}, Litros Anterior: ${data.litros_anterior},
                    Km por Litro: ${data.km_por_litro}
                </p>
            `;
        } else {
            throw new Error("Erro ao procurar abastecimento anterior");
        }
    } catch (error) {
        console.error('Erro:', error);
        alert('Erro ao procurar abastecimento anterior');
    }
}

async function alterarAbastecimento(id) {
    const novaDataReq = prompt("Digite a nova data de requisição (AAAA-MM-DD):");
    const novoKmAtual = prompt("Digite o novo km atual:");
    const novosLitros = prompt("Digite a nova quantidade de litros:");

    try {
        const response = await fetch(`/alterar_abastecimento`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                id: id,
                dataReq: novaDataReq,
                kmAtual: novoKmAtual,
                litros: novosLitros,
            }),
        });

        if (response.ok) {
            alert("Abastecimento alterado com sucesso");
            location.reload(); // Atualiza a página para refletir as alterações
        } else {
            throw new Error("Erro ao alterar o abastecimento");
        }
    } catch (error) {
        console.error('Erro:', error);
        alert('Erro ao alterar o abastecimento');
    }
}

async function consultarMedia() {
    const placa = document.getElementById('mediaPlaca').value;
    if (!placa) {
        alert("Por favor, preencha o campo de placa.");
        return;
    }

    try {
        const response = await fetch(`/consultar_media?placa=${placa}`);
        if (response.ok) {
            const data = await response.json();
            const resultadoDiv = document.getElementById('resultadoMedia');
            resultadoDiv.innerHTML = `
                <p>
                    Veículo: ${data.veiculo_equip}<br>
                    Média Km/Litro: ${data.media_km_por_litro}
                </p>
            `;
        } else {
            throw new Error("Erro ao consultar média Km/Litro");
        }
    } catch (error) {
        console.error('Erro:', error);
        alert('Erro ao consultar média Km/Litro');
    }
}

function openModal(modalId) {
    document.getElementById(modalId).style.display = "block";
    // Clear previous results when opening the modal
    if (modalId === 'consultarMediaModal') {
        document.getElementById('resultadoMedia').innerHTML = '';
    }

    document.getElementById(modalId).style.display = "block";
    // Clear previous results when opening the modal
    if (modalId === 'procurarAbastecimentoModal') {
        document.getElementById('resultadoAbastecimento').innerHTML = '';
    } else if (modalId === 'historicoVeiculoModal') {
        document.getElementById('resultadoHistorico').innerHTML = '';
    }
}
async function cadastrarAbastecimento() {
    const req = document.getElementById('req').value;
    const requisitante = document.getElementById('requisitante').value;
    const kmAtual = parseFloat(document.getElementById('kmAtual').value);
    const dataReq = document.getElementById('dataReq').value;
    const veiculoEquip = document.getElementById('veiculoEquip').value;
    const placa = document.getElementById('placa').value;
    const litros = parseFloat(document.getElementById('litros').value);
    if (!dataReq || !litros || (!veiculoEquip && !placa)) {
        alert("Por favor, preencha os campos obrigatórios: Data, Litros e Veículo ou Placa.");
        return;
    }
    let veiculoEquipFinal = veiculoEquip;
    if (placa) {
        try {
            const response = await fetch(`/obter_veiculo_equip?placa=${placa}`);
            if (response.ok) {
                const data = await response.json();
                veiculoEquipFinal = data.veiculo_equip;
            } else {
                throw new Error("Erro ao buscar veículo por placa");
            }
        } catch (error) {
            console.error('Erro:', error);
            alert('Erro ao buscar veículo por placa');
            return;
        }
    }
    try {
        const response = await fetch(`/cadastrar_abastecimento`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                req: req || null,
                requisitante: requisitante || null,
                kmAtual: kmAtual,
                dataReq: dataReq,
                veiculoEquip: veiculoEquipFinal,
                litros: litros,
                placa: placa
            }),
        });
        const resultadoCadastro = document.getElementById('resultadoCadastro');
        if (response.ok) {
            const data = await response.json();
            alert("Abastecimento cadastrado com sucesso");
            resultadoCadastro.innerHTML = "Abastecimento cadastrado com sucesso!";
            // VerifyIF IThas Anomaly
            if (data.anomalia) {
                const anomaliaBtn = document.getElementById('anomaliaDetectadaBtn');
                anomaliaBtn.style.display = 'inline-block';
                document.getElementById('mensagemAnomalia').innerText = 'Abastecimento Cadastrado está com o Km por Litro abaixo do esperado.';
                document.getElementById('mediaEsperada').innerText = `Média Km/Litro Esperada: ${data.mediaEsperada}`;
                document.getElementById('registroAtual').innerText = `Registro Atual: ${JSON.stringify(data.registroAtual, null, 2)}`;
                document.getElementById('abastecimentoAnterior').innerText = `Abastecimento Anterior: ${JSON.stringify(data.abastecimentoAnterior, null, 2)}`;
            }
        } else {
            throw new Error("Erro ao cadastrar abastecimento");
        }
    } catch (error) {
        resultadoCadastro.innerHTML = `Erro ao cadastrar abastecimento: ${error.message}`;
        console.error('Erro:', error);
        alert('Erro ao cadastrar abastecimento');
    }
}
function openModal(modalId) {
    document.getElementById(modalId).style.display = "block";
    //Clean results Before When Open modal
    if (modalId === 'consultarMediaModal') {
        document.getElementById('resultadoMedia').innerHTML = '';
    } else if (modalId === 'procurarAbastecimentoModal') {
        document.getElementById('resultadoAbastecimento').innerHTML = '';
    } else if (modalId === 'historicoVeiculoModal') {
        document.getElementById('resultadoHistorico').innerHTML = '';
    }
}
function closeModal(modalId) {
    document.getElementById(modalId).style.display = "none";
    if (modalId === 'anomaliaDetectadaModal') {
        document.getElementById('anomaliaDetectadaBtn').style.display = 'none';
    }
}
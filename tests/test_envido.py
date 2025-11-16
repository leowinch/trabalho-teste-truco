import pytest
# 1. Agora só precisamos do MagicMock (para criar objetos falsos)
from unittest.mock import MagicMock
from truco.envido import Envido

# --- Fixtures (Mocks para Dependências) ---
# (Estas fixtures são IDÊNTICAS à versão anterior)

@pytest.fixture
def envido_instance():
    return Envido()

@pytest.fixture
def mock_jogador1():
    j1 = MagicMock()
    j1.pontos = 10
    j1.nome = "Jogador 1"
    j1.retorna_pontos_envido.return_value = 27
    return j1

@pytest.fixture
def mock_jogador2():
    j2 = MagicMock()
    j2.pontos = 8
    j2.nome = "Jogador 2"
    j2.retorna_pontos_envido.return_value = 30
    j2.avaliar_envido.return_value = 1
    return j2

@pytest.fixture
def mock_interface():
    ifc = MagicMock()
    ifc.mostrar_vencedor_envido = MagicMock()
    return ifc

@pytest.fixture
def mock_deps():
    return MagicMock(), MagicMock()




def test_inverter_jogador_bloqueado(envido_instance):
    assert envido_instance.jogador_bloqueado == 0
    envido_instance.inverter_jogador_bloqueado()
    assert envido_instance.jogador_bloqueado == 1
    envido_instance.inverter_jogador_bloqueado()
    assert envido_instance.jogador_bloqueado == 2
    envido_instance.inverter_jogador_bloqueado()
    assert envido_instance.jogador_bloqueado == 1

def test_inicializar_jogador_bloqueado(envido_instance):
    envido_instance.inicializar_jogador_bloqueado(2)
    assert envido_instance.jogador_bloqueado == 2

def test_definir_pontos_jogadores(envido_instance, mock_jogador1, mock_jogador2):
    envido_instance.definir_pontos_jogadores(mock_jogador1, mock_jogador2)
    mock_jogador1.retorna_pontos_envido.assert_called_once()
    mock_jogador2.retorna_pontos_envido.assert_called_once()
    assert envido_instance.jogador1_pontos == 27
    assert envido_instance.jogador2_pontos == 30

def test_resetar(envido_instance):
    envido_instance.valor_envido = 10
    envido_instance.estado_atual = 6
    envido_instance.quem_fugiu = 1
    envido_instance.jogador1_pontos = 30
    envido_instance.resetar()
    assert envido_instance.valor_envido == 2
    assert envido_instance.estado_atual == 0
    assert envido_instance.quem_fugiu == 0
    assert envido_instance.jogador1_pontos == 0


# --- 1. Testes para Mensagens de Erro (Input Inválido) ---
# (Estes testes são IDÊNTICOS à versão anterior)

def test_envido_input_valor_invalido_causa_erro(monkeypatch, envido_instance, mock_jogador1, mock_jogador2, mock_deps):
    monkeypatch.setattr('builtins.input', lambda _: 'abc')
    with pytest.raises(ValueError):
        envido_instance.envido(mock_deps[0], 2, mock_jogador1, mock_jogador2)

# --- 2. Testes para Início e Fim de Loopings (Input) ---
# (Estes testes são IDÊNTICOS à versão anterior)

def test_envido_looping_de_input(monkeypatch, envido_instance, mock_jogador1, mock_jogador2, mock_deps):
    inputs_simulados = ["9", "1"]
    monkeypatch.setattr('builtins.input', lambda _: inputs_simulados.pop(0))

    envido_instance.jogador1_pontos = 27
    envido_instance.jogador2_pontos = 30
    envido_instance.envido(mock_deps[0], 2, mock_jogador1, mock_jogador2)
    assert envido_instance.quem_venceu_envido == 2
    assert mock_jogador2.pontos == 8 + 2

# --- 3. Testes para IF's (Encadeamentos Lógicos) ---
# (Estes testes são IDÊNTICOS à versão anterior)

@pytest.mark.parametrize("j1_pontos, j2_pontos, esperado_vencedor, pontos_j1_final, pontos_j2_final", [
    (30, 27, 1, 12, 8),
    (27, 30, 2, 10, 10),
    (30, 30, 1, 12, 8)
])
def test_avaliar_vencedor_envido_combinacoes(envido_instance, mock_jogador1, mock_jogador2, j1_pontos, j2_pontos, esperado_vencedor, pontos_j1_final, pontos_j2_final):
    envido_instance.jogador1_pontos = j1_pontos
    envido_instance.jogador2_pontos = j2_pontos
    envido_instance.valor_envido = 2
    mock_jogador1.pontos = 10
    mock_jogador2.pontos = 8
    envido_instance.avaliar_vencedor_envido(1, mock_jogador1, mock_jogador2)
    assert envido_instance.quem_venceu_envido == esperado_vencedor
    assert mock_jogador1.pontos == pontos_j1_final
    assert mock_jogador2.pontos == pontos_j2_final


def test_falta_envido_calculo_pontos_j1_pede(envido_instance, mock_jogador1, mock_jogador2):
    """
    Testa o cálculo quando J1 pede Falta Envido.
    """
    # J1 pede. Mock J2 (bot) vai aceitar
    envido_instance.falta_envido(None, 1, mock_jogador1, mock_jogador2)

    # Valor esperado = 12 - j2.pontos (8)
    assert envido_instance.valor_envido == 4


def test_falta_envido_calculo_pontos_j2_pede(envido_instance, mock_jogador1, mock_jogador2, monkeypatch):
    """
    Testa o cálculo quando J2 pede Falta Envido.
    """
    # Simula o J1 (humano) digitando "1"
    monkeypatch.setattr('builtins.input', lambda _: '1')

    # J2 pede. Mock J1 (humano) vai aceitar
    envido_instance.falta_envido(None, 2, mock_jogador1, mock_jogador2)

    # Valor esperado = 12 - j1.pontos (10)
    assert envido_instance.valor_envido == 2

def test_controlador_envido_bloqueado_por_estado(envido_instance, mock_deps, mock_jogador1, mock_jogador2, mock_interface):
    envido_instance.estado_atual = 6
    retorno = envido_instance.controlador_envido(mock_deps[0], mock_deps[1], 6, 1, mock_jogador1, mock_jogador2, mock_interface)
    assert retorno is None

def test_controlador_envido_bloqueado_por_jogador(envido_instance, mock_deps, mock_jogador1, mock_jogador2, mock_interface):
    envido_instance.jogador_bloqueado = 1
    retorno = envido_instance.controlador_envido(mock_deps[0], mock_deps[1], 6, 1, mock_jogador1, mock_jogador2, mock_interface)
    assert retorno is None



def test_envido_bot_recusa(envido_instance, mock_jogador1, mock_jogador2, mock_deps):
    mock_jogador2.avaliar_envido.return_value = 0
    envido_instance.envido(mock_deps[0], 1, mock_jogador1, mock_jogador2)
    assert envido_instance.quem_fugiu == 2
    assert mock_jogador1.pontos == 10 + 1
    assert mock_jogador2.pontos == 8

def test_real_envido_humano_aceita(monkeypatch, envido_instance, mock_jogador1, mock_jogador2, mock_deps):
    monkeypatch.setattr('builtins.input', lambda _: '1')
    envido_instance.jogador1_pontos = 27
    envido_instance.jogador2_pontos = 30
    envido_instance.real_envido(mock_deps[0], 2, mock_jogador1, mock_jogador2)
    assert envido_instance.quem_fugiu == 0
    assert envido_instance.quem_venceu_envido == 2
    assert mock_jogador1.pontos == 10
    assert mock_jogador2.pontos == 8 + 5



def test_fluxo_controlador_envido_para_real_envido(
    envido_instance, mock_jogador1, mock_jogador2, mock_deps, mock_interface,
    monkeypatch # Precisamos do monkeypatch para a resposta do J1
):
    """
    Testa o fluxo correto via CONTROLADOR:
    1. J1 pede Envido (tipo 6)
    2. J2 (bot) aumenta para Real Envido (escolha 2)
    3. J1 (humano) aceita (escolha 1)
    """

    # Configura o J2 (bot) para responder '2' (Aumentar para Real Envido)
    # Ele só será chamado uma vez (na lógica do 'envido')
    mock_jogador2.avaliar_envido.return_value = 2

    # Configura o J1 (humano) para responder '1' (Aceitar)
    # quando o 'real_envido' chamar o input()
    monkeypatch.setattr('builtins.input', lambda _: '1')

    # J1 (quem_pediu=1) chama Envido (tipo=6)
    envido_instance.controlador_envido(
        mock_deps[0], mock_deps[1], 6, 1,
        mock_jogador1, mock_jogador2, mock_interface
    )


    # O estado deve parar em Real Envido (7), pois J1 aceitou
    assert envido_instance.estado_atual == 7
    assert envido_instance.valor_envido == 5 # Valor do Real Envido


    # O fluxo de bloqueio correto é:
    # - Início: 0
    # - controlador_envido(quem_pediu=1) -> inicializar(1) -> bloqueado = 1
    # - envido() -> J2 responde '2' (aumenta) -> inverter_jogador_bloqueado() -> bloqueado = 2
    # - real_envido(quem_pediu=2) -> J1 (humano) responde '1' -> termina.
    # O estado final do bloqueio deve ser 2.
    assert envido_instance.jogador_bloqueado == 2

    # 3. Verificação dos Pontos
    # O controlador chamou 'definir_pontos_jogadores'
    # J1 tem 27, J2 tem 30. J2 venceu.
    assert envido_instance.quem_venceu_envido == 2
    # J2 ganha os 5 pontos do Real Envido
    assert mock_jogador2.pontos == 8 + 5

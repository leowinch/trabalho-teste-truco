import pytest
from unittest.mock import MagicMock
from truco.truco import Truco

# --- Fixtures (Mocks) ---

@pytest.fixture
def truco_instance():
    return Truco()

@pytest.fixture
def mock_jogador1():
    j1 = MagicMock()
    j1.pontos = 10
    j1.nome = "Jogador 1"
    return j1

@pytest.fixture
def mock_jogador2():
    j2 = MagicMock()
    j2.pontos = 8
    j2.nome = "Jogador 2"
    # Resposta padrão do bot (1 = Aceitar)
    j2.avaliar_truco.return_value = 1
    return j2

@pytest.fixture
def mock_deps():
    # Mocks para 'cbr' e 'dados' que são apenas repassados
    return MagicMock(), MagicMock()



def test_pedir_truco_input_invalido_causa_erro(monkeypatch, truco_instance, mock_jogador1, mock_jogador2, mock_deps):

    # Simula o J1 (humano) digitando "teste"
    monkeypatch.setattr('builtins.input', lambda _: 'teste')

    with pytest.raises(ValueError):
        truco_instance.pedir_truco(mock_deps[0], 2, mock_jogador1, mock_jogador2)

# --- Testes para Início e Fim de Loopings ---

def test_pedir_truco_looping_de_input(monkeypatch, truco_instance, mock_jogador1, mock_jogador2, mock_deps):

    inputs_simulados = ["9", "5", "1"]
    monkeypatch.setattr('builtins.input', lambda _: inputs_simulados.pop(0))

    # J2 pede, J1 (humano) responde
    retorno = truco_instance.pedir_truco(mock_deps[0], 2, mock_jogador1, mock_jogador2)

    assert retorno is True

def test_pedir_vale_quatro_looping_de_input(monkeypatch, truco_instance, mock_jogador1, mock_jogador2, mock_deps):

    inputs_simulados = ["2", "0"]
    monkeypatch.setattr('builtins.input', lambda _: inputs_simulados.pop(0))

    # J2 pede, J1 (humano) responde
    retorno = truco_instance.pedir_vale_quatro(mock_deps[0], 2, mock_jogador1, mock_jogador2)

    # O teste deve retornar False (Recusado) e J2 ganha 3 pontos
    assert retorno is False
    assert mock_jogador2.pontos == 8 + 3

# --- Testes para IF's ---

def test_inverter_jogador_bloqueado_logica(truco_instance):

    assert truco_instance.jogador_bloqueado == 0

    # 0 -> 1
    truco_instance.inverter_jogador_bloqueado()
    assert truco_instance.jogador_bloqueado == 1

    # 1 -> 2
    truco_instance.inverter_jogador_bloqueado()
    assert truco_instance.jogador_bloqueado == 2

    # 2 -> 1
    truco_instance.inverter_jogador_bloqueado()
    assert truco_instance.jogador_bloqueado == 1



def test_controlador_truco_bloqueado_por_estado(truco_instance, mock_deps, mock_jogador1, mock_jogador2):
    truco_instance.estado_atual = "vale_quatro"
    retorno = truco_instance.controlador_truco(mock_deps[0], mock_deps[1], 1, mock_jogador1, mock_jogador2)
    assert retorno is None

def test_controlador_truco_bloqueado_por_jogador(truco_instance, mock_deps, mock_jogador1, mock_jogador2):

    truco_instance.jogador_bloqueado = 1 # J1 está bloqueado
    retorno = truco_instance.controlador_truco(mock_deps[0], mock_deps[1], 1, mock_jogador1, mock_jogador2)
    assert retorno is None

def test_pedir_truco_bot_recusa(truco_instance, mock_jogador1, mock_jogador2, mock_deps):

    # Configura o J2 (bot) para recusar (0)
    mock_jogador2.avaliar_truco.return_value = 0

    # J1 pede
    retorno = truco_instance.pedir_truco(mock_deps[0], 1, mock_jogador1, mock_jogador2)

    # J1 ganha 1 ponto
    assert mock_jogador1.pontos == 10 + 1
    assert retorno is False

def test_pedir_retruco_humano_aceita(monkeypatch, truco_instance, mock_jogador1, mock_jogador2, mock_deps):
    # J1 (humano) responde "1" (Aceitar)
    monkeypatch.setattr('builtins.input', lambda _: '1')

    # J2 pede
    retorno = truco_instance.pedir_retruco(mock_deps[0], 2, mock_jogador1, mock_jogador2)

    assert retorno is True
    assert truco_instance.valor_aposta == 3 # 'pedir_retruco' define o valor como 3
    assert mock_jogador1.pontos == 10 # Ninguém ganha pontos ainda
    assert mock_jogador2.pontos == 8

def test_pedir_truco_aumenta_para_retruco(truco_instance, mock_jogador1, mock_jogador2, mock_deps, monkeypatch):
    # J2 (bot) responde '2' (Aumentar) na primeira chamada (truco)
    # e '1' (Aceitar) na segunda chamada (retruco)
    mock_jogador2.avaliar_truco.return_value = 2

    # Simula J1 aceitar retruco do bot
    monkeypatch.setattr('builtins.input', lambda _: '1')

    # J1 pede Truco
    retorno = truco_instance.pedir_truco(mock_deps[0], 1, mock_jogador1, mock_jogador2)

    # O fluxo deve terminar em "retruco" aceito
    assert retorno is True
    assert truco_instance.estado_atual == "retruco"
    assert truco_instance.valor_aposta == 3

    # Verificação de bloqueio:
    # 1. 'pedir_truco' (quem_pediu=1) -> 'self.jogador_bloqueado = 1'
    # 2. 'escolha == 2' -> 'inverter_jogador_bloqueado()' (1 -> 2)
    # 3. 'pedir_retruco' (quem_pediu=2) -> 'self.jogador_bloqueado = 2' (na lógica 'else')
    assert truco_instance.jogador_bloqueado == 2

# --- Testes para Chamadas de Função  ---

@pytest.mark.parametrize("quem_pediu, estado_esperado", [
    (1, "truco"),   # J1 pede, bot aceita
    (2, "truco")    # J2 pede, humano aceita
])

def test_controlador_truco_inicia_fluxo(monkeypatch, truco_instance, mock_jogador1, mock_jogador2, mock_deps, quem_pediu, estado_esperado):

    assert truco_instance.estado_atual == ""

    # Simula o J1 (humano) aceitando, caso J2 peça
    monkeypatch.setattr('builtins.input', lambda _: '1')

    # J2 (bot) já aceita por padrão na fixture

    retorno = truco_instance.controlador_truco(mock_deps[0], mock_deps[1], quem_pediu, mock_jogador1, mock_jogador2)

    assert retorno is True
    assert truco_instance.estado_atual == estado_esperado


def test_resetar(truco_instance):

    truco_instance.valor_aposta = 4
    truco_instance.jogador_bloqueado = 2
    truco_instance.estado_atual = "vale_quatro"

    # Chama o reset
    truco_instance.resetar()

    # Verifica os valores padrão do __init__
    assert truco_instance.valor_aposta == 1
    assert truco_instance.jogador_bloqueado == 0
    assert truco_instance.estado_atual == ""



# --- Testes para Retornos de Função ---

def test_retornar_valor_aposta(truco_instance):

    truco_instance.valor_aposta = 3
    assert truco_instance.retornar_valor_aposta() == 3

@pytest.mark.parametrize("escolha_humana, esperado_retorno", [
    ('0', False), # Recusar
    ('1', True)   # Aceitar
])

def test_pedir_vale_quatro_retorna_bool(monkeypatch, truco_instance, mock_jogador1, mock_jogador2, mock_deps, escolha_humana, esperado_retorno):

    monkeypatch.setattr('builtins.input', lambda _: escolha_humana)

    # J2 pede, J1 (humano) responde
    retorno = truco_instance.pedir_vale_quatro(mock_deps[0], 2, mock_jogador1, mock_jogador2)

    assert retorno is esperado_retorno

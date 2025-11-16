import pytest
from unittest.mock import MagicMock
from truco.flor import Flor

# --- Fixtures (Mocks) ---

@pytest.fixture
def flor_instance():
    """Retorna uma instância limpa da classe Flor para cada teste."""
    return Flor()

@pytest.fixture
def mock_jogador1():
    j1 = MagicMock()
    j1.pontos = 10
    j1.nome = "Jogador 1"
    j1.flor = False
    # Se o jogador já pediu flor (para o 'pedir_flor' rastrear)
    j1.pediu_flor = False
    j1.retorna_pontos_envido.return_value = 26
    return j1

@pytest.fixture
def mock_jogador2():
    """Mock do Jogador 2."""
    j2 = MagicMock()
    j2.pontos = 8
    j2.nome = "Jogador 2"
    j2.flor = False
    j2.pediu_flor = False
    j2.retorna_pontos_envido.return_value = 29
    return j2

@pytest.fixture
def mock_interface():
    ifc = MagicMock()
    ifc.mostrar_vencedor_flor = MagicMock()
    return ifc



def test_decisao_jogador(monkeypatch, flor_instance):

    # Simula o usuário digitando "abc"
    monkeypatch.setattr('builtins.input', lambda _: 'abc')

    with pytest.raises(ValueError):
        flor_instance.decisao_jogador()



def test_decisao_jogador_looping_de_input(monkeypatch, flor_instance):

    inputs_simulados = ["9", "5", "0"]
    monkeypatch.setattr('builtins.input', lambda _: inputs_simulados.pop(0))

    # Executa o método
    retorno = flor_instance.decisao_jogador()

    # O teste deve consumir "9", "5" e parar no "0"
    assert retorno is False






def test_pedir_flor_bloqueado_se_estado_nao_vazio(flor_instance, mock_jogador1, mock_jogador2, mock_interface):
    # Define um estado
    flor_instance.estado_atual = "Flor"

    # Tenta pedir de novo
    flor_instance.pedir_flor(1, mock_jogador1, mock_jogador2, mock_interface)

    # Verifica se nada aconteceu (ex: pontos não foram somados)
    assert mock_jogador1.pontos == 10
    assert mock_jogador2.pontos == 8
    # Verifica se a interface não foi chamada
    mock_interface.mostrar_vencedor_flor.assert_not_called()





def test_pedir_flor_jogador1_apenas_tem_flor(flor_instance, mock_jogador1, mock_jogador2, mock_interface):

    mock_jogador1.flor = True
    mock_jogador2.flor = False

    flor_instance.pedir_flor(1, mock_jogador1, mock_jogador2, mock_interface)


    assert mock_jogador1.pontos == 10 + 3
    assert flor_instance.quem_venceu_flor == 1
    mock_interface.mostrar_vencedor_flor.assert_called_once_with(1, "Jogador 1", "Jogador 2", 3)

def test_pedir_flor_jogador2_apenas_tem_flor(flor_instance, mock_jogador1, mock_jogador2, mock_interface):
    mock_jogador1.flor = False
    mock_jogador2.flor = True

    flor_instance.pedir_flor(2, mock_jogador1, mock_jogador2, mock_interface)


    assert mock_jogador2.pontos == 8 + 3
    assert flor_instance.quem_venceu_flor == 2
    mock_interface.mostrar_vencedor_flor.assert_called_once_with(2, "Jogador 1", "Jogador 2", 3)

def test_pedir_flor_ambos_tem_flor_contraflor_recusa(monkeypatch, flor_instance, mock_jogador1, mock_jogador2, mock_interface):

    mock_jogador1.flor = True
    mock_jogador2.flor = True
    # Força a lógica a NÃO ir para "Contraflor e Resto"
    mock_jogador1.pontos = 5
    mock_jogador2.pontos = 4

    # Simula a recusa (0)
    monkeypatch.setattr('builtins.input', lambda _: '0')

    flor_instance.pedir_flor(1, mock_jogador1, mock_jogador2, mock_interface)

    assert mock_jogador2.pontos == 4 + 4
    assert flor_instance.estado_atual == "Contraflor"




def test_pedir_flor_ambos_tem_flor_contraflor_resto_aceita(monkeypatch, flor_instance, mock_jogador1, mock_jogador2, mock_interface):

    mock_jogador1.flor = True
    mock_jogador2.flor = True

    mock_jogador1.pontos = 10
    mock_jogador2.pontos = 5

    # Simula o aceite (1)
    monkeypatch.setattr('builtins.input', lambda _: '1')

    flor_instance.pedir_flor(1, mock_jogador1, mock_jogador2, mock_interface)

    assert flor_instance.estado_atual == "Contraflor e Resto"
    # J2 (29 pts envido) vence J1 (26 pts envido)
    assert flor_instance.quem_venceu_flor == 2
    # J2 ganha 3 pontos (valor_flor)
    assert mock_jogador2.pontos == 5 + 3
    mock_interface.mostrar_vencedor_flor.assert_called_once()



@pytest.mark.parametrize("j1_env_pts, j2_env_pts, esperado_vencedor, j1_final_pts, j2_final_pts", [
    (30, 27, 1, 16, 8), # J1 vence
    (27, 30, 2, 10, 14), # J2 vence
    (30, 30, 1, 16, 8)  # J1 vence empate
])
def test_contraflor_logica_vencedor(flor_instance, mock_jogador1, mock_jogador2, j1_env_pts, j2_env_pts, esperado_vencedor, j1_final_pts, j2_final_pts):
    """Testa todas as combinações do 'if/elif/else' em 'contraflor'."""
    mock_jogador1.retorna_pontos_envido.return_value = j1_env_pts
    mock_jogador2.retorna_pontos_envido.return_value = j2_env_pts
    mock_jogador1.pontos = 10
    mock_jogador2.pontos = 8

    # Executa
    flor_instance.contraflor(1, mock_jogador1, mock_jogador2)

    assert flor_instance.valor_flor == 6
    assert flor_instance.quem_venceu_flor == esperado_vencedor
    assert mock_jogador1.pontos == j1_final_pts
    assert mock_jogador2.pontos == j2_final_pts



def test_pedir_flor_define_atributo_jogador1(flor_instance, mock_jogador1, mock_jogador2, mock_interface):
    """Testa se 'pedir_flor' altera 'jogador1.pediu_flor' quando quem_pediu=1."""
    mock_jogador1.flor = True
    flor_instance.pedir_flor(1, mock_jogador1, mock_jogador2, mock_interface)
    assert mock_jogador1.pediu_flor is True
    assert mock_jogador2.pediu_flor is False

def test_pedir_flor_define_atributo_jogador2(flor_instance, mock_jogador1, mock_jogador2, mock_interface):
    """Testa se 'pedir_flor' altera 'jogador2.pediu_flor' quando quem_pediu=2."""
    mock_jogador2.flor = True
    flor_instance.pedir_flor(2, mock_jogador1, mock_jogador2, mock_interface)
    assert mock_jogador1.pediu_flor is False
    assert mock_jogador2.pediu_flor is True

def test_resetar_flor_restaura_padroes(flor_instance):
    # Modifica o estado
    flor_instance.valor_flor = 6
    flor_instance.estado_atual = "Contraflor"
    flor_instance.quem_venceu_flor = 1

    # Chama o reset
    flor_instance.resetar_flor()

    # Verifica os padrões do __init__
    assert flor_instance.valor_flor == 3
    assert flor_instance.estado_atual == ""
    assert flor_instance.quem_venceu_flor == 0




def test_decisao_jogador_retorna_true(monkeypatch, flor_instance):
    """Testa o 'return True' para a entrada '1'."""
    monkeypatch.setattr('builtins.input', lambda _: '1')
    assert flor_instance.decisao_jogador() is True

def test_decisao_jogador_retorna_false(monkeypatch, flor_instance):
    """Testa o 'return False' para a entrada '0'."""
    monkeypatch.setattr('builtins.input', lambda _: '0')
    assert flor_instance.decisao_jogador() is False

def test_pedir_flor_retorna_none_se_bloqueado(flor_instance, mock_jogador1, mock_jogador2, mock_interface):
    """Testa o 'return' (None) da guarda no início de 'pedir_flor'."""
    flor_instance.estado_atual = "Flor"
    retorno = flor_instance.pedir_flor(1, mock_jogador1, mock_jogador2, mock_interface)
    assert retorno is None

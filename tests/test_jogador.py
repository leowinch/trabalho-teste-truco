import pytest
from unittest.mock import MagicMock
from truco.jogador import Jogador
from truco.carta import Carta
from truco.baralho import Baralho



@pytest.fixture
def jogador():
    return Jogador(nome="jogador teste")

@pytest.fixture
def baralho():
    return Baralho()



def test_jogador_init(jogador):
    assert jogador.nome == "jogador teste"
    assert jogador.mao == []
    assert jogador.pontos == 0
    assert jogador.rodadas == 0
    assert jogador.envido == 0
    assert jogador.flor is False
    assert jogador.pediu_truco is False

def test_adicionar_pontos(jogador):
    jogador.adicionar_pontos(5)
    assert jogador.pontos == 5
    jogador.adicionar_pontos(10)
    assert jogador.pontos == 15
    jogador.adicionar_pontos(-3)
    assert jogador.pontos == 12

def test_adicionar_rodada(jogador):
    jogador.adicionar_rodada()
    assert jogador.rodadas == 1
    jogador.adicionar_rodada()
    assert jogador.rodadas == 2

def test_resetar(jogador):
    jogador.pontos = 10;

    jogador.resetar()

    assert jogador.rodadas == 0
    assert jogador.mao == []
    assert jogador.flor is False
    assert jogador.pediu_truco is False
    # pontos não restam
    assert jogador.pontos == 10



@pytest.mark.parametrize("cartas_mao, esperado", [
    ([Carta("1", "ESPADAS"), Carta("12", "ESPADAS"), Carta("3", "ESPADAS")], True),
    ([Carta("1", "ESPADAS"), Carta("12", "ESPADAS"), Carta("3", "COPAS")], False),
])
def test_checa_flor(jogador, cartas_mao, esperado):
    jogador.mao = cartas_mao
    assert jogador.checa_flor() is esperado

def test_calcula_envido(jogador):
    mao1 = [Carta("2", "OUROS"), Carta("12", "COPAS"), Carta("3", "OUROS")]
    assert jogador.calcula_envido(mao1) == 25

    mao2 = [Carta("10", "COPAS"), Carta("1", "ESPADA"), Carta("5", "BASTOS")]
    assert jogador.calcula_envido(mao2) == 5




def test_criar_mao(jogador, baralho):

    jogador.criar_mao(baralho)

    assert len(jogador.mao) == 3
    assert len(baralho.cartas) == 37 # 40 - 3
    # Verifica se o envido foi calculado e armazenado
    assert jogador.envido == jogador.calcula_envido(jogador.mao)

def test_jogar_carta(jogador):
    c1 = Carta("1", "OUROS")
    c2 = Carta("2", "COPAS")
    c3 = Carta("12", "ESPADAS")
    jogador.mao = [c1, c2, c3]

    # Ação: Jogar a carta do meio (
    carta_jogada = jogador.jogar_carta(1)

    # Verificação
    assert carta_jogada == c2
    assert len(jogador.mao) == 2
    assert jogador.mao == [c1, c3]




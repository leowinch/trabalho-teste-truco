from truco.cbr import Cbr
import pytest
import sys

@pytest.fixture
def cbr():
    return Cbr()


def test_jogar_carta(cbr):
    # Testa se retorna o índice certo da carta para jogar
    # a última rodada 1 vencida pelo bot ele jogou uma carta de valor 1
    assert cbr.jogar_carta(1, [1, 4, 12]) == 0

    # a última rodada 2 vencida pelo bot ele jogou uma carta de valor 2
    assert cbr.jogar_carta(2, [4, 11, 10]) == 0

    # a última rodada 3 vencida pelo bot ele jogou uma carta de valor 7
    assert cbr.jogar_carta(3, [9, 3, 6]) == 2



def test_truco(cbr):

    assert cbr.truco(2, 1, 0) == 0
    assert cbr.truco(1, 2, 0) == 0

def test_envido(cbr):

    # > 5 pontos e perdendo
    assert cbr.envido(0, 2, 12, True) == 8
    # > 5 pontos e ganhando
    assert cbr.envido(0, 2, 12, False) == 6
    # humano pediu
    assert cbr.envido(6, 1, 0, True) == 1
    assert cbr.envido(6, 1, -3, True) == 1
    assert cbr.envido(7, 1, 0, False) == 0

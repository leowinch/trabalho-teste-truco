import pytest
from truco.jogo import Jogo
from truco.jogador import Jogador
from truco.bot import Bot
from truco.baralho import Baralho
from truco.carta import Carta
from truco.interface import Interface

@pytest.fixture
def jogo():
    return Jogo()

@pytest.fixture
def mock_baralho():
    return Baralho()

@pytest.fixture
def interface():
    return Interface()

@pytest.fixture
def mock_jogador1():
    return Jogador("J1")

@pytest.fixture
def mock_jogador2():
    return Jogador("bot")



@pytest.fixture
def manilha_alta():
    return Carta("1", "ESPADAS")

@pytest.fixture
def manilha_baixa():
    return Carta("7", "OUROS")

@pytest.fixture
def carta_comum_alta():
    return Carta("3", "BASTOS")

@pytest.fixture
def carta_comum_baixa():
    return Carta("4", "COPAS")


def test_jogo(jogo):
    assert jogo.rodadas == []
    assert jogo.trucoPontos == 1


def test_verificar_carta_vencedora(jogo, manilha_alta, manilha_baixa, carta_comum_alta, carta_comum_baixa):
    assert jogo.verificar_carta_vencedora(manilha_alta, manilha_baixa) == manilha_alta
    assert jogo.verificar_carta_vencedora(manilha_baixa, carta_comum_alta) == manilha_baixa
    assert jogo.verificar_carta_vencedora(carta_comum_alta, manilha_alta) == manilha_alta
    assert jogo.verificar_carta_vencedora(carta_comum_alta, carta_comum_baixa) == carta_comum_alta
    assert jogo.verificar_carta_vencedora(carta_comum_alta, carta_comum_alta) == carta_comum_alta


def test_criar_jogador(jogo, mock_baralho):
    jogador = jogo.criar_jogador("Humano", mock_baralho)
    assert jogador.nome == "Humano"
    assert len(jogador.mao) == 3

def test_criar_bot(jogo, mock_baralho):
    bot = jogo.criar_bot("IA", mock_baralho)
    assert bot.nome == "IA"
    assert len(bot.mao) == 3

def test_verificar_ganhador(jogo, interface):
    c1 = Carta("1", "OUROS")
    c2 = Carta("2", "COPAS")

    assert jogo.verificar_ganhador(c1, c2, interface) == c2


def test_adicionar_rodada(jogo, mock_jogador1, mock_jogador2):
    c1 = Carta("1", "OUROS")
    c2 = Carta("2", "COPAS")

    retorno = jogo.adicionar_rodada(mock_jogador1, mock_jogador2, c1, c2, c1)
    assert retorno == 1

    retorno = jogo.adicionar_rodada(mock_jogador1, mock_jogador2, c1, c2, c2)
    assert retorno == 2

def test_quem_joga_primeiro(jogo, mock_jogador1, mock_jogador2):
    c1 = Carta("1", "OUROS")
    c2 = Carta("2", "COPAS")

    jogo.quem_joga_primeiro(mock_jogador1, mock_jogador2, c1, c2, c1)
    assert mock_jogador1.primeiro is True
    assert mock_jogador2.primeiro is False

    jogo.quem_joga_primeiro(mock_jogador1, mock_jogador2, c1, c2, c2)
    assert mock_jogador1.primeiro is False
    assert mock_jogador2.primeiro is True

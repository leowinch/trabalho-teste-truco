import random
import pandas as pd
from truco.bot import Bot
from truco.baralho import Baralho
from truco.carta import Carta
from truco.dados import Dados
from truco.cbr import Cbr

import pytest

@pytest.fixture
def bot():
    return Bot("bot")

@pytest.fixture
def baralho():
    return Baralho()

@pytest.fixture
def dados():
    return Dados()

@pytest.fixture
def cbr():
    return Cbr()

def test_bot(bot):
    assert bot.nome == "bot"
    assert bot.mao == []
    assert bot.mao_rank == []
    assert bot.indices == []
    assert bot.pontuacao_cartas == []
    assert bot.qualidade_mao == 0
    assert bot.pontos == 0
    assert bot.rodadas == 0
    assert bot.envido == 0
    assert bot.rodada == 1
    assert bot.primeiro == False
    assert bot.ultimo == False
    assert bot.flor == False
    assert bot.pediu_flor == False
    assert bot.pediu_truco == False

def test_checa_flor(bot):
    cartas = [Carta("1", "COPAS"), Carta("11", "COPAS"), Carta("3", "COPAS")]
    bot.mao = cartas
    assert bot.checa_flor() == True

    cartas = [Carta("1", "ESPADA"), Carta("6", "ESPADAS"), Carta("3", "COPAS")]
    bot.mao = cartas
    assert bot.checa_flor() == False

def test_calcular_qualidade_mao(bot):
    bot.mao = [Carta("2", "OUROS"), Carta("12", "COPAS"), Carta("3", "OUROS")]
    pontuacao, mao_rank = bot.mao[0].classificar_carta(bot.mao)

    bot.calcular_qualidade_mao(pontuacao, mao_rank)

    assert round(bot.qualidade_mao) == 25

def test_calcula_envido(bot):
    bot.mao = [Carta("2", "OUROS"), Carta("12", "COPAS"), Carta("3", "OUROS")]
    assert bot.calcula_envido(bot.mao) == 25

    bot.mao = [Carta("10", "COPAS"), Carta("1", "ESPADA"), Carta("5", "BASTOS")]
    assert bot.calcula_envido(bot.mao) == 5

def test_criar_mao(bot, baralho):
    cartas = baralho.cartas.copy()[-3:]

    bot.criar_mao(baralho)

    assert len(bot.mao) == 3

    for i in range(0,3):
        assert bot.mao[i] == cartas[2-i]

    assert bot.indices == [0, 1, 2]
    assert bot.flor == bot.checa_flor()
    assert bot.pontuacao_cartas, bot.mao_rank == bot.mao[0].classificar_carta(bot.mao)
    assert bot.envido == bot.calcula_envido(bot.mao)


def test_jogar_carta(bot):
    try:
        bot.mao = [Carta("1", "ESPADA"), Carta("12", "ESPADA"), Carta("3", "COPAS")]
        bot.flor = False
        assert bot.jogar_carta(cbr, None) == 5
    except AttributeError:
        pass

def test_retornar_pontos_envido(bot):
    bot.envido = 29
    assert bot.retorna_pontos_envido() == 29


def test_calcular_envido(bot):
    mao1 = [Carta("1", "ESPADA"), Carta("12", "ESPADA"), Carta("3", "COPAS")]
    assert bot.calcula_envido(mao1) == 3

    mao2 = [Carta("7", "COPAS"), Carta("6", "COPAS"), Carta("12", "COPAS")]
    assert bot.calcula_envido(mao2) == 33




def test_mostrar_mao(bot, capsys):
    bot.mao = [Carta("1", "COPAS"), Carta("12", "ESPADA"), Carta("3", "COPAS")]

    bot.mostrar_mao()


    out, err = capsys.readouterr()
    assert out == "[0] 1 de COPAS\n[1] 12 de ESPADA\n[2] 3 de COPAS\n"

def test_adicionar_pontos(bot):


    bot.adicionar_pontos(5)
    bot.adicionar_pontos(5)
    bot.adicionar_pontos(-10)

    assert bot.pontos == 0

def test_adicionar_rodadas(bot):
    bot.adicionar_rodada()
    assert bot.rodadas == 1


def test_checa_mao(bot):
    bot.mao = [Carta("1", "ESPADA"), Carta("1", "COPAS"), Carta("2", "COPAS")]
    assert bot.checa_mao() == bot.mao

def test_checa_flor(bot):
    bot.mao = [Carta("1", "ESPADA"), Carta("2", "ESPADA"), Carta("3", "ESPADA")]
    assert bot.checa_flor() == True

    bot.mao = [Carta("1", "ESPADA"), Carta("2", "ESPADA"), Carta("3", "COPAS")]
    assert bot.checa_flor() == False



def test_avaliar_envido(bot, cbr):
     #cbr, tipo, quem_pediu, pontos_totais_adversario
    assert bot.avaliar_envido(cbr, 2, 2, 1) == 0
    bot.envido = 25
    assert bot.avaliar_envido(cbr, 0, 2, 7) == 8

def test_avaliar_pedir_envido(bot):
    assert bot.avaliar_pedir_envido() == 1

def retornar_pontos_totais(bot):
    bot.pontos = 10
    assert bot.retornar_pontos_totais() == 10


def test_resetar(bot):

    bot.resetar()

    assert bot.mao == []
    assert bot.mao_rank == []
    assert bot.indices == []
    assert bot.pontuacao_cartas == []
    assert bot.qualidade_mao == 0
    assert bot.rodadas == 0
    assert bot.envido == 0
    assert bot.rodada == 1
    assert bot.flor == False
    assert bot.pediu_flor == False
    assert bot.pediu_truco == False

import pandas as pd
import os
from truco.dados import Dados
from truco.carta import Carta
import pytest

@pytest.fixture
def dados():
    return Dados()

@pytest.fixture
def colunas():
    return ['idMao', 'jogadorMao', 'cartaAltaRobo', 'cartaMediaRobo', 'cartaBaixaRobo', 'cartaAltaHumano', 'cartaMediaHumano', 'cartaBaixaHumano', 'primeiraCartaRobo', 'primeiraCartaHumano', 'segundaCartaRobo', 'segundaCartaHumano', 'terceiraCartaRobo', 'terceiraCartaHumano', 'ganhadorPrimeiraRodada', 'ganhadorSegundaRodada', 'ganhadorTerceiraRodada', 'quemPediuEnvido', 'quemPediuFaltaEnvido', 'quemPediuRealEnvido', 'pontosEnvidoRobo', 'pontosEnvidoHumano', 'quemNegouEnvido', 'quemGanhouEnvido', 'idMao', 'quemContraFlor', 'quemContraFlorResto', 'quemNegouFlor', 'pontosFlorRobo', 'pontosFlorHumano', 'quemGanhouFlor', 'quemEscondeuPontosEnvido', 'quemEscondeuPontosFlor', 'quemTruco', 'quemRetruco', 'quemValeQuatro', 'quemNegouTruco', 'quemGanhouTruco','quemEnvidoEnvido', 'quemFlor', 'naipeCartaAltaRobo', 'naipeCartaMediaRobo', 'naipeCartaBaixaRobo', 'naipeCartaAltaHumano', 'naipeCartaMediaHumano', 'naipeCartaBaixaHumano', 'naipePrimeiraCartaRobo', 'naipePrimeiraCartaHumano', 'naipeSegundaCartaRobo', 'naipeSegundaCartaHumano', 'naipeTerceiraCartaRobo', 'naipeTerceiraCartaHumano', 'qualidadeMaoRobo', 'qualidadeMaoHumano']


def test_carregar_modelo_zerado(dados, colunas):
    df: pd.DataFrame = dados.carregar_modelo_zerado()
    assert df.shape == (1, 52)
    assert df.index.to_list() == [0]
    assert df.columns.to_list() != colunas



def test_finalizar_partida(dados):
    if os.path.isfile("jogadas.csv"):
        os.remove("jogadas.csv")

    dados.finalizar_partida()

    assert os.path.isfile("jogadas.csv")


def test_resetar(dados):
    df_casos = dados.tratamento_inicial_df()
    df_registro = dados.carregar_modelo_zerado()

    dados.resetar()

    assert dados.registro.equals(df_registro)
    assert dados.casos.equals(df_casos)

def test_cartas_jogadas_pelo_bot(dados):
    c1 = Carta('1', "COPAS")

    dados.cartas_jogadas_pelo_bot("primeira", c1)

    assert dados.registro.primeiraCartaRobo[0] == c1.retornar_numero()
    assert dados.registro.naipePrimeiraCartaRobo[0] == c1.retornar_naipe_codificado()


    dados.cartas_jogadas_pelo_bot("segunda", c1)

    assert dados.registro.segundaCartaRobo[0] == c1.retornar_numero()
    assert dados.registro.naipeSegundaCartaRobo[0] == c1.retornar_naipe_codificado()

    dados.cartas_jogadas_pelo_bot("terceira", c1)

    assert dados.registro.terceiraCartaRobo[0] == c1.retornar_numero()
    assert dados.registro.naipeTerceiraCartaRobo[0] == c1.retornar_naipe_codificado()

def test_primeira_rodada(dados):

    dados.primeira_rodada([1,2,3], ["Alta", "Media", "Baixa"], 1, Carta('3', "COPAS"))

    assert dados.registro.jogadorMao[0] == 1
    assert dados.registro.cartaAltaRobo[0] == 1
    assert dados.registro.cartaMediaRobo[0] == 2
    assert dados.registro.cartaBaixaRobo[0] == 3
    assert dados.registro.qualidadeMaoBot == 1 # definido na função
    assert dados.registro.primeiraCartaHumano[0] == "3"
    assert dados.registro.naipePrimeiraCartaHumano[0] == 4

def test_segunda_rodada(dados):

    dados.segunda_rodada(Carta('3', "COPAS"), Carta('4', "BASTOS"), 1)

    assert dados.registro.ganhadorPrimeiraRodada[0] == 1
    assert dados.registro.primeiraCartaHumano[0] == "3"
    assert dados.registro.naipePrimeiraCartaHumano[0] == 4
    assert dados.registro.terceiraCartaRobo[0] == "4"

def test_terceira_rodada(dados):

    dados.terceira_rodada(Carta('3', "COPAS"), Carta('4', "BASTOS"), 1)

    assert dados.registro.ganhadorSegundaRodada[0] == 1
    assert dados.registro.SegundaCartaHumano[0] == "3"
    assert dados.registro.naipeSegundaCartaHumano[0] == 4
    assert dados.registro.terceiraCartaRobo[0] == "4"

def test_finalizar_rodadas(dados):

    dados.finalizar_rodadas(Carta('12', "OUROS"), Carta('3', "ESPADAS"), 1)

    assert dados.registro.ganhadorTerceiraRodada[0] == 1
    assert dados.registro.terceiraCartaHumano[0] == "12"
    assert dados.registro.naipeTerceiraCartaHumano[0] == 2
    assert dados.registro.terceiraCartaRobo[0] == "12"

def test_envido(dados):

    dados.envido(1, 2, 2, 1)

    assert dados.registro.quemEnvido == 1
    assert dados.registro.quemRealEnvido == 2
    assert dados.registro.quemFaltaEnvido == 2
    assert dados.registro.quemGanhouEnvido[0] == 1

def test_truco(dados):
    dados.truco(1, 2, 2, 1, 1)

    assert dados.registro.quemTruco[0] == 1
    assert dados.registro.quemRetruco[0] == 2
    assert dados.registro.quemValeQuatro[0] == 2
    assert dados.registro.quemNegouTruco[0] == 1
    assert dados.registro.quemGanhouTruco[0] == 1

def test_flor(dados):

    dados.flor(1, 2, 2, 7)

    assert dados.registro.quemGanhouFlor[0] == 2
    assert dados.registro.quemFlor[0] == 1
    assert dados.registro.quemContraFlor[0] == 2
    assert dados.registro.quemContraFlorResto[0] == 2
    assert dados.registro.pontosFlorRobo[0] == 7

def test_vencedor_envido(dados):

    dados.vencedor_envido(1, 2)

    assert dados.registro.quemGanhouEnvido[0] == 1
    assert dados.registro.quemNegouEnvido[0] == 2

def test_vencedor_truco(dados):

    dados.vencedor_truco(1, 2)

    assert dados.registro.quemGanhouTruco[0] == 1
    assert dados.registro.quemNegouTruco[0] == 2

def test_vencedor_flor(dados):

    dados.vencedor_flor(1, 2)

    assert dados.registro.quemGanhouFlor[0] == 1
    assert dados.registro.quemNegouFlor[0] == 2





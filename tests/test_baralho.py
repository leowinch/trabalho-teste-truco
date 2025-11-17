import pytest
import random
from truco.baralho import Baralho
from truco.carta import Carta



@pytest.fixture
def baralho_novo():
    return Baralho()

@pytest.fixture
def baralho_vazio():
    b = Baralho()
    b.cartas = []
    return b



def test_criar_baralho_inicio_loop(baralho_novo):
    primeira_carta = baralho_novo.cartas[0]
    assert primeira_carta.numero == 1
    assert primeira_carta.naipe == "ESPADAS"

def test_criar_baralho_fim_loop(baralho_novo):
    ultima_carta = baralho_novo.cartas[-1]
    assert ultima_carta.numero == 12
    assert ultima_carta.naipe == "BASTOS"

def test_criar_baralho_contagem_total_apos_loop(baralho_novo):
    assert len(baralho_novo.cartas) == 40


def test_criar_baralho_if_condicao_verdadeira_menor(baralho_novo):

    # Procura por qualquer carta de número 7
    tem_carta_7 = any(c.numero == 7 for c in baralho_novo.cartas)
    assert tem_carta_7

def test_criar_baralho_if_condicao_verdadeira_maior(baralho_novo):

    # Procura por qualquer carta de número 10
    tem_carta_10 = any(c.numero == 10 for c in baralho_novo.cartas)
    assert tem_carta_10

def test_criar_baralho_if_condicao_falsa(baralho_novo):
    # Procura por cartas 8 ou 9
    tem_carta_8 = any(c.numero == 8 for c in baralho_novo.cartas)
    tem_carta_9 = any(c.numero == 9 for c in baralho_novo.cartas)

    assert not tem_carta_8
    assert not tem_carta_9


def test_resetar_limpa_listas_de_estado(baralho_novo):
    baralho_novo.retirar_carta()
    assert len(baralho_novo.cartas) == 39

    baralho_novo.manilhas = [Carta(1, "ESPADAS")]
    assert len(baralho_novo.manilhas) == 1

    baralho_novo.resetar()

    assert len(baralho_novo.cartas) == 0
    assert len(baralho_novo.manilhas) == 0
    assert len(baralho_novo.vira) == 0




def test_retirar_carta_retorna_objeto_carta(baralho_novo):
    carta_retirada = baralho_novo.retirar_carta()
    assert isinstance(carta_retirada, Carta)

def test_retirar_carta_remove_carta_do_baralho(baralho_novo):
    tamanho_antes = len(baralho_novo.cartas)
    baralho_novo.retirar_carta()
    tamanho_depois = len(baralho_novo.cartas)

    assert tamanho_depois == tamanho_antes - 1
    assert tamanho_depois == 39


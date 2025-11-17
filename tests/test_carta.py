import pytest
import truco.carta as carta_modulo
from truco.carta import Carta
import sys

@pytest.fixture
def mock_pontos_reais(monkeypatch):


    MANILHA = {
        "1 de ESPADAS": 52,
        "1 de BASTOS": 50,
        "7 de ESPADAS": 42,
        "7 de OUROS": 40
    }

    CARTAS_VALORES = {
        "3": 24,
        "2": 16,
        "1": 12,
        "12": 8,
        "11": 7,
        "10": 6,
        "7": 4,
        "6": 3,
        "5": 2,
        "4": 1
    }

    ENVIDO = {
        "3": 3,
        "2": 2,
        "1": 1,
        "12": 0,
        "11": 0,
        "10": 0,
        "7": 7,
        "6": 6,
        "5": 5,
        "4": 4
    }

    monkeypatch.setattr(carta_modulo, 'MANILHA', MANILHA)
    monkeypatch.setattr(carta_modulo, 'CARTAS_VALORES', CARTAS_VALORES)
    monkeypatch.setattr(carta_modulo, 'ENVIDO', ENVIDO)

    return {
        "MANILHA": MANILHA,
        "CARTAS_VALORES": CARTAS_VALORES,
        "ENVIDO": ENVIDO
    }


@pytest.fixture
def carta_instance(mock_pontos_reais):

    return Carta(numero=None, naipe=None)



def test_retornar_numero():
    carta = Carta(numero=5, naipe='COPAS')
    assert carta.retornar_numero() == 5

def test_retornar_naipe_codificado(carta_instance):
    carta_instance.naipe = 'ESPADAS'
    assert carta_instance.retornar_naipe_codificado() == 1
    carta_instance.naipe = 'OUROS'
    assert carta_instance.retornar_naipe_codificado() == 2
    carta_instance.naipe = 'BASTOS'
    assert carta_instance.retornar_naipe_codificado() == 3
    carta_instance.naipe = 'COPAS'
    assert carta_instance.retornar_naipe_codificado() == 4
    carta_instance.naipe = 'NAIPE INVALIDO'
    assert carta_instance.retornar_naipe_codificado() is None

def test_retornar_pontos_carta_manilha(carta_instance):
    """Testa o retorno da pontuação da manilha mais forte (1 de Espadas)."""
    carta = Carta(numero=1, naipe='ESPADAS')
    assert carta_instance.retornar_pontos_carta(carta) == 52

def test_retornar_pontos_carta_normal(carta_instance):
    carta = Carta(numero=3, naipe='BASTOS')
    assert carta_instance.retornar_pontos_carta(carta) == 24

def test_retornar_pontos_envido_figura(carta_instance):
    carta_figura = Carta(numero=12, naipe='OUROS')
    assert carta_instance.retornar_pontos_envido(carta_figura) == 0

def test_retornar_pontos_envido_carta_normal(carta_instance):
    """Testa o retorno do valor nominal para cartas do Envido (7)."""
    carta_normal = Carta(numero=7, naipe='COPAS')
    assert carta_instance.retornar_pontos_envido(carta_normal) == 7


@pytest.mark.parametrize("c1_num, c1_naipe, c2_num, c2_naipe, esperada", [
    # Manilha vs Manilha (1 Espadas > 1 Bastos) - Início de looping (1ª combinação de if)
    (1, 'ESPADAS', 1, 'BASTOS', (1, 'ESPADAS')),
    # Manilha vs Manilha (7 Ouros < 7 Espadas) - 2ª combinação de if/elif
    (7, 'OUROS', 7, 'ESPADAS', (7, 'ESPADAS')),
    # C1 é Manilha (1 Bastos vs 3 normal) - 3ª combinação de if/elif
    (1, 'BASTOS', 3, 'COPAS', (1, 'BASTOS')),
    # C2 é Manilha (3 normal vs 7 Ouros) - 4ª combinação de if/elif
    (3, 'COPAS', 7, 'OUROS', (7, 'OUROS')),
    # Ambos normais (3 vs 2) - Início do bloco 'else' (Combinação 5)
    (3, 'OUROS', 2, 'BASTOS', (3, 'OUROS')),
    # Ambos normais (10 vs 11) - Fim do bloco 'else' (Combinação 6)
    (10, 'BASTOS', 11, 'COPAS', (11, 'COPAS')),
    # Empate entre cartas normais (Retorna a segunda, conforme o código)
    (3, 'BASTOS', 3, 'COPAS', (3, 'COPAS')),
])
def test_verificar_carta_alta_combinacoes(carta_instance, c1_num, c1_naipe, c2_num, c2_naipe, esperada):
    """Testa todas as combinações de if/elif na lógica de 'verificar_carta_alta'."""
    carta_01 = Carta(numero=c1_num, naipe=c1_naipe)
    carta_02 = Carta(numero=c2_num, naipe=c2_naipe)

    resultado = carta_instance.verificar_carta_alta(carta_01, carta_02)

    assert resultado.numero == esperada[0]
    assert resultado.naipe == esperada[1]


@pytest.mark.parametrize("c1_num, c1_naipe, c2_num, c2_naipe, esperada", [
    # Manilha vs Manilha (1 Espadas > 1 Bastos) - Início de looping (1ª combinação de if)
    (1, 'ESPADAS', 1, 'BASTOS', (1, 'BASTOS')),
    # Manilha vs Manilha (7 Ouros < 7 Espadas) - 2ª combinação de if/elif
    (7, 'OUROS', 7, 'ESPADAS', (7, 'OUROS')),
    # C1 é Manilha (1 Bastos vs 3 normal) - 3ª combinação de if/elif
    (1, 'BASTOS', 3, 'COPAS', (3, 'COPAS')),
    # C2 é Manilha (3 normal vs 7 Ouros) - 4ª combinação de if/elif
    (3, 'COPAS', 7, 'OUROS', (3, 'COPAS')),
    # Ambos normais (3 vs 2) - Início do bloco 'else' (Combinação 5)
    (3, 'OUROS', 2, 'BASTOS', (2, 'BASTOS')),
    # Ambos normais (10 vs 11) - Fim do bloco 'else' (Combinação 6)
    (10, 'BASTOS', 11, 'COPAS', (10, 'BASTOS')),
    # Empate entre cartas normais (Retorna a segunda, conforme o código)
    (3, 'BASTOS', 3, 'COPAS', (3, 'COPAS')),
])
def test_verificar_carta_baixa_combinacoes(carta_instance, c1_num, c1_naipe, c2_num, c2_naipe, esperada):
    """Testa todas as combinações de if/elif na lógica de 'verificar_carta_alta'."""
    carta_01 = Carta(numero=c1_num, naipe=c1_naipe)
    carta_02 = Carta(numero=c2_num, naipe=c2_naipe)

    resultado = carta_instance.verificar_carta_baixa(carta_01, carta_02)

    assert resultado.numero == esperada[0]
    assert resultado.naipe == esperada[1]




def test_classificar_carta_cenario_completo(carta_instance):
    """
    Testa classificar 3 cartas (Manilha, Normal Alta, Normal Baixa) e a pontuação.
    Cobre o looping de 3 iterações (início, meio e fim).
    """
    # Pontuação: 1 de Ouros (40), 3 de Copas (24), 4 de Espadas (1)
    c_manilha = Carta(numero=7, naipe='OUROS')  # Manilha (40 pontos) - Alta
    c_normal_alta = Carta(numero=3, naipe='COPAS') # Normal (24 pontos) - Média
    c_normal_baixa = Carta(numero=4, naipe='ESPADAS') # Normal (1 ponto) - Baixa

    # Ordem de entrada: [Baixa, Manilha, Média]
    cartas = [c_normal_baixa, c_manilha, c_normal_alta]

    lista_pontos, lista_classificacao = carta_instance.classificar_carta(cartas)

    # Verificação da Ordem do Looping (i=0, i=1, i=2)
    # i=0 (c_normal_baixa)
    assert lista_pontos[0] == 1
    assert lista_classificacao[0] == 'Baixa'

    # i=1 (c_manilha)
    assert lista_pontos[1] == 40
    assert lista_classificacao[1] == 'Alta'

    # i=2 (c_normal_alta) - Deve cair no último 'if not' (Média)
    assert lista_pontos[2] == 24
    assert lista_classificacao[2] == 'Media'




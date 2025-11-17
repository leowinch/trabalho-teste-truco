import pytest
from pytest_mock import mocker
from unittest.mock import MagicMock
import pandas as pd
from sklearn.neighbors import NearestNeighbors


from truco.carta import Carta
from truco.jogador import Jogador
from truco.bot import Bot
from truco.truco import Truco
from truco.envido import Envido
from truco.flor import Flor
from truco.baralho import Baralho
from truco.jogo import Jogo
from truco.cbr import Cbr
from truco.dados import Dados
import truco.carta as carta_modulo # <<< CORREÇÃO 1: Módulo importado


class MockInterface(MagicMock):
    pass


class Partida:
    def __init__(self, interface):
        self.jogo = Jogo()
        self.baralho = Baralho()
        self.cbr = Cbr()
        self.interface = interface
        self.dados = Dados()
        self.truco = Truco()
        self.flor = Flor()
        self.envido = Envido()
        self.jogador1 = None
        self.jogador2 = None
        self.vencedor_partida = None

    def iniciar_jogo(self, nome_j1, nome_j2):
        self.baralho.embaralhar()
        self.jogador1 = self.jogo.criar_jogador(nome_j1, self.baralho)
        self.jogador2 = self.jogo.criar_bot(nome_j2, self.baralho)
        self.jogador1.primeiro = True
        self.jogador2.ultimo = True

    def reiniciar_rodada(self):
        self.dados.finalizar_partida()
        self.jogador1.resetar()
        self.jogador2.resetar()
        self.baralho.resetar()
        self.baralho.criar_baralho()
        self.baralho.embaralhar()
        self.jogador1.criar_mao(self.baralho)
        self.jogador2.criar_mao(self.baralho)
        self.envido.resetar()
        self.truco.resetar()
        self.flor.resetar_flor()

    def processar_acao_humano(self, acao_id, mocker_bot=None):
        jogador = self.jogador1
        oponente = self.jogador2

        if mocker_bot:
            mocker.patch.object(self.jogador2, 'avaliar_truco', return_value=mocker_bot.get('truco'))
            mocker.patch.object(self.jogador2, 'avaliar_envido', return_value=mocker_bot.get('envido'))

        if acao_id == 9:
            oponente.adicionar_pontos(self.truco.retornar_valor_aposta())
            self.reiniciar_rodada()
            return 'DESISTIU'

        elif acao_id == 4:
            jogador.pediu_truco = True
            chamou = self.truco.controlador_truco(self.cbr, self.dados, 1, jogador, oponente)
            if chamou is False:
                self.reiniciar_rodada()
                return 'TRUCO_RECUSADO'
            return 'TRUCO_ACEITO'

        elif acao_id == 6:
            self.envido.controlador_envido(self.cbr, self.dados, 6, 1, jogador, oponente, self.interface)
            if self.envido.retornar_quem_fugiu() > 0:
                return 'ENVIDO_RECUSADO'
            return 'ENVIDO_ACEITO'

        elif acao_id == 5:
            if not jogador.checa_flor():
                return 'FLOR_INVALIDA'
            self.flor.pedir_flor(1, jogador, oponente, self.interface)


            if self.flor.quem_venceu_flor == 0 and (jogador.flor and oponente.flor):
                return 'FLOR_RECUSADA'
            return 'FLOR_ACEITA'

        elif 0 <= acao_id <= 2:
            if acao_id < len(jogador.checa_mao()):
                return jogador.jogar_carta(acao_id)
            else:
                return 'CARTA_INVALIDA'

        return 'ACAO_INVALIDA'

    def checar_fim_de_jogo(self):
        if self.jogador1.pontos >= 12:
            self.vencedor_partida = self.jogador1
            return True
        if self.jogador2.pontos >= 12:
            self.vencedor_partida = self.jogador2
            return True
        return False


@pytest.fixture
def partida(monkeypatch):
    mock_df = pd.DataFrame([{"idMao": 0, "ganhadorPrimeiraRodada": 0, "terceiraCartaRobo": 0, "quemGanhouTruco": 2, "qualidadeMaoHumano": 0, "pontosEnvidoHumano": 0, "quemPediuRealEnvido": 0, "quemPediuFaltaEnvido": 0, "quemGanhouEnvido": 0}])
    monkeypatch.setattr(pd, "read_csv", lambda *args, **kwargs: mock_df)

    # Mock para 'kneighbors' do Cbr para evitar erro
    mock_knn = MagicMock()
    mock_knn.kneighbors.return_value = (None, [[0]]) # Retorna índice 0
    mock_fit = MagicMock(return_value=mock_knn)
    mock_nn_class = MagicMock(return_value=MagicMock(fit=mock_fit))
    # Mocka a importação do NearestNeighbors dentro do módulo cbr
    monkeypatch.setattr("truco.cbr.NearestNeighbors", mock_nn_class)

    partida_teste = Partida(interface=MockInterface())
    partida_teste.iniciar_jogo("Humano", "Bot")

    # Mock para 'finalizar_partida' não tentar escrever em disco
    monkeypatch.setattr(partida_teste.dados, 'finalizar_partida', lambda: None)

    return partida_teste


def test_rf01_iniciar_partida(partida):
    assert partida.jogador1 is not None
    assert partida.jogador2 is not None
    assert partida.jogador1.nome == "Humano"
    assert partida.jogador2.nome == "Bot"
    assert partida.jogador1.pontos == 0
    assert partida.jogador2.pontos == 0


def test_rf02_distribuir_cartas(partida):
    assert len(partida.jogador1.checa_mao()) == 3
    assert len(partida.jogador2.checa_mao()) == 3



def test_rf04_fazer_jogada_jogador(partida):
    if not partida.jogador1.checa_mao():
        partida.jogador1.mao = [Carta(1, "ESPADAS"), Carta(2, "COPAS"), Carta(3, "BASTOS")]

    carta_jogada = partida.jogador1.checa_mao()[0]
    mao_size_antes = len(partida.jogador1.checa_mao())

    carta_retornada = partida.processar_acao_humano(0)

    assert mao_size_antes == 3
    assert len(partida.jogador1.checa_mao()) == 2
    assert carta_retornada == carta_jogada


def test_rf06_determinar_ganhador_rodada(partida, monkeypatch):
    test_manilhas = {'1 de ESPADAS': 13}
    test_valores = {'4': 0}
    monkeypatch.setattr('truco.jogo.MANILHA', test_manilhas)
    monkeypatch.setattr('truco.jogo.CARTAS_VALORES', test_valores)

    espadao = Carta(1, "ESPADAS")
    quatro_paus = Carta(4, "BASTOS")

    vencedor = partida.jogo.verificar_carta_vencedora(espadao, quatro_paus)
    assert vencedor == espadao


def test_rf09_desistir_ir_ao_baralho(partida):
    assert partida.jogador1.pontos == 0
    assert partida.jogador2.pontos == 0

    resultado = partida.processar_acao_humano(9)

    assert resultado == 'DESISTIU'
    assert partida.jogador1.pontos == 0
    assert partida.jogador2.pontos == 1


def test_rf10_encerrar_partida(partida):
    partida.jogador1.adicionar_pontos(11)
    assert partida.checar_fim_de_jogo() is False

    partida.jogador1.adicionar_pontos(1)

    assert partida.jogador1.pontos == 12
    assert partida.checar_fim_de_jogo() is True
    assert partida.vencedor_partida == partida.jogador1


def test_rf11_pedir_truco(partida, mocker):
    mocker.patch.object(partida.jogador2, 'avaliar_truco', return_value=1)

    assert partida.truco.valor_aposta == 1
    assert partida.truco.estado_atual == ""

    resultado = partida.processar_acao_humano(4)

    assert resultado == 'TRUCO_ACEITO'
    assert partida.truco.estado_atual == "truco"
    assert partida.truco.jogador_bloqueado == 1


def test_rf14_gerenciar_recusa_de_aposta_truco(partida, mocker):
    mocker.patch.object(partida.jogador2, 'avaliar_truco', return_value=0)

    assert partida.jogador1.pontos == 0
    assert partida.jogador2.pontos == 0

    resultado = partida.processar_acao_humano(4)

    assert resultado == 'TRUCO_RECUSADO'
    assert partida.jogador1.pontos == 1
    assert partida.jogador2.pontos == 0


def test_rf16_gerenciar_aumento_aposta_retruco(partida, mocker):
    mocker.patch.object(partida.jogador2, 'avaliar_truco', return_value=2)

    mocker.patch('builtins.input', return_value='1') # 1 = Aceitar

    resultado_bot = partida.truco.controlador_truco(partida.cbr, partida.dados, 1, partida.jogador1, partida.jogador2)

    assert partida.truco.valor_aposta == 3
    assert partida.truco.estado_atual == "retruco"


def test_rf17_solicitar_envido(partida, mocker):
    mocker.patch.object(partida.jogador2, 'avaliar_envido', return_value=1)
    partida.jogador1.mao = [Carta(7, 'OUROS'), Carta(6, 'OUROS'), Carta(1, 'BASTOS')]
    partida.jogador2.mao = [Carta(5, 'COPAS'), Carta(4, 'COPAS'), Carta(1, 'ESPADAS')]
    partida.jogador1.envido = 33
    partida.jogador2.envido = 29

    resultado = partida.processar_acao_humano(6)

    assert resultado == 'ENVIDO_ACEITO'
    assert partida.envido.estado_atual == 6


def test_rf20_gerenciar_recusa_envido(partida, mocker):
    mocker.patch.object(partida.jogador2, 'avaliar_envido', return_value=0)
    partida.jogador1.mao = [Carta(7, 'OUROS'), Carta(6, 'OUROS'), Carta(1, 'PAUS')]

    resultado = partida.processar_acao_humano(6)

    assert resultado == 'ENVIDO_RECUSADO'
    assert partida.jogador1.pontos == 1
    assert partida.jogador2.pontos == 0


def test_rf21_rf22_verificar_e_somar_pontos_envido(partida, mocker, monkeypatch):
    # Mock das constantes de Envido
    test_envido = {'7': 7, '6': 6, '5': 5, '4': 4, '1': 1}
    monkeypatch.setattr(carta_modulo, 'ENVIDO', test_envido)

    mocker.patch.object(partida.jogador2, 'avaliar_envido', return_value=1)

    partida.jogador1.mao = [Carta(7, 'OUROS'), Carta(6, 'OUROS'), Carta(1, 'BASTOS')]
    partida.jogador2.mao = [Carta(5, 'COPAS'), Carta(4, 'COPAS'), Carta(1, 'ESPADAS')]
    partida.jogador1.envido = partida.jogador1.calcula_envido(partida.jogador1.mao)
    partida.jogador2.envido = partida.jogador2.calcula_envido(partida.jogador2.mao)

    assert partida.jogador1.envido == 33
    assert partida.jogador2.envido == 29

    partida.processar_acao_humano(6)

    assert partida.envido.quem_venceu_envido == 1
    assert partida.jogador1.pontos == 2
    assert partida.jogador2.pontos == 0


def test_rf27_rf30_solicitar_flor_com_flor(partida, mocker):

    partida.jogador1.mao = [Carta(7, 'OUROS'), Carta(6, 'OUROS'), Carta(1, 'OUROS')]
    partida.jogador2.mao = [Carta(5, 'COPAS'), Carta(4, 'COPAS'), Carta(1, 'ESPADAS')]
    partida.jogador1.flor = partida.jogador1.checa_flor()
    partida.jogador2.flor = partida.jogador2.checa_flor()

    assert partida.jogador1.flor is True
    assert partida.jogador2.flor is False


    mocker.patch.object(partida.flor, 'decisao_jogador', return_value=True)

    resultado = partida.processar_acao_humano(5)

    assert resultado == 'FLOR_ACEITA'
    assert partida.jogador1.pontos == 3
    assert partida.flor.quem_venceu_flor == 1


def test_rf30_nao_permitir_pedir_flor_sem_flor(partida):
    partida.jogador1.mao = [Carta(7, 'OUROS'), Carta(6, 'ESPADAS'), Carta(1, 'OUROS')]
    partida.jogador1.flor = partida.jogador1.checa_flor()

    assert partida.jogador1.flor is False

    resultado = partida.processar_acao_humano(5)

    assert resultado == 'FLOR_INVALIDA'
    assert partida.jogador1.pontos == 0


def test_rf24_tratar_empate_primeira_rodada(partida, monkeypatch):
    # Mock das constantes
    test_manilhas = {}
    test_valores = {'7': 4, '1': 12, '2': 16, '3': 24, '4': 0}
    monkeypatch.setattr('truco.jogo.MANILHA', test_manilhas)
    monkeypatch.setattr('truco.jogo.CARTAS_VALORES', test_valores)

    # Mock para 'retornar_numero' da classe Carta
    def mock_retornar_numero(self):
        return str(self.numero)
    monkeypatch.setattr(Carta, "retornar_numero", mock_retornar_numero)

    carta_j1 = Carta(7, 'COPAS')
    carta_j2 = Carta(7, 'BASTOS')

    partida.jogador1.mao = [carta_j1, Carta(1, 'BASTOS'), Carta(2, 'BASTOS')]
    partida.jogador2.mao = [carta_j2, Carta(3, 'BASTOS'), Carta(4, 'BASTOS')]

    ganhador = partida.jogo.verificar_carta_vencedora(carta_j1, carta_j2)

    assert ganhador == carta_j1

"""Estima o deslocamento da câmera de baixo entre quadros (fluxo óptico global).

Só analisa imagens; não envia comandos. Sinal: dx > 0, chão anda para a direita na imagem; dy > 0, para baixo.
A correspondência com o movimento do drone depende da montagem e precisa de calibração.
"""
import cv2
import numpy as np


def desloca(anterior, atual):
    a = np.float32(anterior)
    b = np.float32(atual)
    janela = cv2.createHanningWindow(a.shape[::-1], cv2.CV_32F)
    (dx, dy), confianca = cv2.phaseCorrelate(a, b, janela)
    return dx, dy, confianca


def direcao(dx, dy, limite=0.5):
    """Texto simples para o sentido do chão na imagem."""
    if max(abs(dx), abs(dy)) < limite:
        return "parado"
    if abs(dx) >= abs(dy):
        return "direita" if dx > 0 else "esquerda"
    return "baixo" if dy > 0 else "cima"

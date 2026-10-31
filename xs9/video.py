"""Vídeo do drone. Só envia o início e recibos com comando NEUTRO; nunca liga motor.

Uso:
  python3 -m xs9.video 0 10 saida/   # câmera 0 ou 1, segundos, pasta dos JPEGs
"""
import pathlib
import socket
import sys
import time

from . import protocolo as p
from .jpeg_headers import HEADERS

IFACE = b"wlp2s0"
PERIODO_RECIBO = 0.025


def quadros(camera=p.CAM_FRONTAL, segundos=float("inf")):
    """Gera bytes JPEG com a câmera pedida."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BINDTODEVICE, IFACE)
    s.bind(("", 0))
    s.settimeout(0.003)
    slots, feitos = {}, set()
    seq_comando, ultimo, proximo_inicio = 0, 0.0, 0.0
    fim = time.time() + segundos
    try:
        while time.time() < fim:
            agora = time.time()
            if not feitos and agora >= proximo_inicio:
                s.sendto(p.INICIAR_VIDEO, p.DRONE)
                proximo_inicio = agora + 0.1
            try:
                f = p.ler_fragmento(s.recv(2048))
            except socket.timeout:
                f = None
            if f:
                q = slots.setdefault(f["seq"], {"total": f["total"], "partes": {}})
                q["partes"][f["indice"]] = f["dados"]
                if len(q["partes"]) == q["total"] and f["seq"] not in feitos:
                    feitos.add(f["seq"])
                    if f["qualidade"] in HEADERS:
                        yield p.montar_jpeg(HEADERS[f["qualidade"]], f["largura"], f["altura"],
                                            [q["partes"][i] for i in range(q["total"])])
            if feitos and time.time() - ultimo > PERIODO_RECIBO:
                ultimo = time.time()
                seq_comando += 1
                s.sendto(p.recibo(seq_comando, _vagas(slots, feitos), camera), p.DRONE)
                for k in [k for k in slots if k < max(feitos) - 8]:
                    del slots[k]
    finally:
        s.close()


def _vagas(slots, feitos):
    topo = max(feitos)
    ocupadas = {(seq + 3) % 4: seq for seq in slots if topo - seq < 5}
    vagas = []
    for i in range(4):
        seq = ocupadas.get(i)
        if seq is None or (seq in feitos and topo - seq >= 4):
            vagas.append(p.vaga(i + 1 if seq is None else seq + 4, 3))
            continue
        q = slots[seq]
        bits = bytearray(b"\xff" * (((q["total"] + 31) // 32) * 4))
        for b in range(q["total"]):
            if b not in q["partes"]:
                bits[b // 8] &= ~(1 << (b % 8)) & 0xFF
        vagas.append(p.vaga(seq, 1 if seq in feitos else 0, bytes(bits)))
    return vagas


def main():
    camera, segundos = int(sys.argv[1]), float(sys.argv[2])
    pasta = pathlib.Path(sys.argv[3])
    pasta.mkdir(parents=True, exist_ok=True)
    n = 0
    for jpeg in quadros(camera, segundos):
        (pasta / f"{n:05d}.jpg").write_bytes(jpeg)
        n += 1
    print(f"{n} quadros em {pasta}")


if __name__ == "__main__":
    main()

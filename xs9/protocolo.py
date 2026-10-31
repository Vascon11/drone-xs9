"""Protocolo do drone (UDP 192.168.169.1:8800), recuperado do app RC FPV 1.7.0 e testado ao vivo.

Só monta bytes: não abre sockets. O comando de voo vai dentro do recibo curto (libuav_tc.so,
build_send_ack), no byte 16. Veja docs/protocolo.md.
"""
import struct

DRONE = ("192.168.169.1", 8800)
INICIAR_VIDEO = bytes.fromhex("ef000400")
CAM_FRONTAL, CAM_BAIXO = 0, 1
TAMANHO_FRAGMENTO = 1024
OFFSET_PAYLOAD = 0x38


def comando(roll=0x80, pitch=0x80, acelerador=0x80, yaw=0x80, cmd=0):
    """Quadro de 8 bytes. Ordem dos eixos provável, sentido ainda não confirmado."""
    corpo = bytes([roll, pitch, acelerador, yaw, cmd])
    xor = 0
    for b in corpo:
        xor ^= b
    return b"\x66" + corpo + bytes([xor, 0x99])


NEUTRO = comando()


def vaga(seq, status, bitmap=b""):
    return struct.pack("<QII", seq, status, 16 + len(bitmap)) + bitmap


def recibo(seq_comando, vagas, camera=CAM_FRONTAL, cmd=NEUTRO):
    if len(cmd) != 8:
        raise ValueError("o recibo curto leva comando de 8 bytes")
    b = bytearray(b"\xef\x02\x00\x00\x02\x02\x00\x01")
    b += bytes([len(vagas)]) + bytes(3) + struct.pack("<I", seq_comando) + cmd
    b += bytes([0x19, 0x32, 0x23, 0x4B, camera]) + bytes(3)
    b += b"".join(vagas) + bytes(8)
    struct.pack_into("<H", b, 2, len(b))
    return bytes(b)


def ler_fragmento(pacote):
    """Retorna dict do fragmento JPEG (`93 01`), ou None para outros pacotes."""
    if pacote[:2] != b"\x93\x01" or len(pacote) < OFFSET_PAYLOAD:
        return None
    seq = struct.unpack_from("<Q", pacote, 8)[0]
    indice, total, tamanho, largura, altura, qualidade = struct.unpack_from("<IIIHHB", pacote, 0x20)
    return {"seq": seq, "indice": indice, "total": total, "tamanho": tamanho, "largura": largura,
            "altura": altura, "qualidade": qualidade, "dados": pacote[OFFSET_PAYLOAD:]}


def montar_jpeg(cabecalho, largura, altura, partes):
    j = bytearray(cabecalho)
    struct.pack_into(">HH", j, 0x91, altura, largura)
    return bytes(j) + b"".join(partes) + b"\xff\xd9"

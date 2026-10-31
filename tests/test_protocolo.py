import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from xs9 import protocolo as p  # noqa: E402
from xs9.jpeg_headers import HEADERS  # noqa: E402
from xs9.video import _vagas  # noqa: E402


class TestProtocolo(unittest.TestCase):
    def test_comandos_conhecidos(self):
        self.assertEqual(p.NEUTRO.hex(), "6680808080000099")
        self.assertEqual(p.comando(cmd=4).hex(), "6680808080040499")
        self.assertEqual(p.comando(roll=0xf0).hex(), "66f0808080007099")

    def test_recibo_curto(self):
        r = p.recibo(7, [p.vaga(2, 1, b"\xff" * 4), p.vaga(3, 3)], p.CAM_BAIXO)
        self.assertEqual(r[:2], b"\xef\x02")
        self.assertEqual(int.from_bytes(r[2:4], "little"), len(r))
        self.assertEqual(r[8], 2)
        self.assertEqual(r[16:24], p.NEUTRO)
        self.assertEqual(r[0x1c], p.CAM_BAIXO)
        self.assertEqual(len(r), 32 + 20 + 16 + 8)

    def test_fragmento_e_jpeg(self):
        pk = bytearray(0x38 + 4)
        pk[:2] = b"\x93\x01"
        pk[0x20:0x31] = bytes.fromhex("0100000002000000080000008002e00132")
        pk[-4:] = b"abcd"
        f = p.ler_fragmento(bytes(pk))
        self.assertEqual((f["indice"], f["total"], f["largura"], f["altura"], f["qualidade"]), (1, 2, 640, 480, 50))
        j = p.montar_jpeg(HEADERS[50], 640, 480, [b"xx"])
        self.assertTrue(j.startswith(b"\xff\xd8") and j.endswith(b"xx\xff\xd9"))

    def test_vagas(self):
        slots = {1: {"total": 2, "partes": {0: b"", 1: b""}}}
        v = _vagas(slots, {1})
        self.assertEqual(len(v), 4)


if __name__ == "__main__":
    unittest.main()

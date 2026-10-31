import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from xs9.fluxo import desloca, direcao  # noqa: E402


class TestFluxo(unittest.TestCase):
    def test_translacao(self):
        rng = np.random.default_rng(0)
        base = rng.random((240, 320))
        for sx, sy in ((5, 0), (-4, 3), (0, -6)):
            dx, dy, c = desloca(base, np.roll(base, (sy, sx), (0, 1)))
            self.assertAlmostEqual(dx, sx, delta=0.5)
            self.assertAlmostEqual(dy, sy, delta=0.5)

    def test_textos(self):
        self.assertEqual(direcao(0.1, 0.1), "parado")
        self.assertEqual(direcao(3, 1), "direita")
        self.assertEqual(direcao(-1, -3), "cima")


if __name__ == "__main__":
    unittest.main()

# drone-xs9

Controle pelo computador de um drone dobrável genérico (logo parecido com "XS9 MAX", app **RC FPV**),
com duas câmeras e sem GPS aparente. Projeto irmão do [`drone-predator`](https://github.com/Vascon11/drone-predator).

## O que funciona

| Recurso | Status |
|---|---|
| Vídeo JPEG 640×480, ~20 fps | ✅ confirmado ao vivo |
| Trocar câmera (0 frontal, 1 de baixo) | ✅ confirmado ao vivo |
| Comando `0x01` liga motores; `0x04` para | ✅ sem hélices, medido por áudio |
| Eixos | ⚠️ ordem provável, sentido desconhecido |
| Voo pelo computador | ❌ nunca testado |

## Uso

Conecte o Wi-Fi na rede `WIFI_8K-XXXXXX` e use a interface `wlp2s0` (ou ajuste `IFACE`):

```bash
python3 -m xs9.video 0 10 saida/frontal   # 10 s da câmera frontal
python3 -m xs9.video 1 10 saida/baixo     # 10 s da câmera de baixo
python3 tests/test_protocolo.py           # testes sem drone
```

O cliente de vídeo envia só o comando neutro. Este repositório não tem script que ligue motores.

> ⚠️ Teste de motor só sem hélices e com corte físico à mão. Primeiro voo só pelo controle, ao ar livre,
> longe de pessoas. O botão de pouso do controle desce, não corta os motores no ar.

Veja [`docs/protocolo.md`](docs/protocolo.md).

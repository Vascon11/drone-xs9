# Como o drone funciona

Legenda: ✅ confirmado ao vivo · 📄 só análise do app · 🌐 de projeto público.
App `com.cooingdv.rcfpv` 1.7.0, protegido por 360 Jiagu; o código Java não foi decifrado. A análise veio de
`libuav_gl.so` e `libuav_tc.so`.

## Rede ✅

| Item | Valor |
|---|---|
| SSID | `WIFI_8K-F4E9E4` (aberto) |
| IP | `192.168.169.1` |
| TCP | Nenhuma porta aberta |
| UDP | 8800 |

## Vídeo ✅

- `ef 00 04 00` inicia o vídeo. Sem recibo, o drone manda 2 quadros e para.
- Drone → cliente: `93 01 <len u16>`, seq u64 em 8, índice/total/tamanho u32 em 0x20/0x24/0x28,
  largura/altura u16 em 0x2c/0x2e, qualidade u8 em 0x30, payload em 0x38 (fragmentos de 1024 bytes).
- Cada quadro JPEG = cabeçalho da qualidade + fragmentos + `ff d9`. Tamanho observado 640×480, Q 25/50.

## Recibo curto ✅

```
ef 02 <len u16> 02 02 00 01 <n vagas> 00 00 00 <seq u32> <comando 8> 19 32 23 4b <câmera> 00 00 00 <vagas> 00×8
```

Vaga: seq u64, status u32, tamanho u32 (16 + bitmap), bitmap. Status 0 parcial, 1 completo, 3 pedir quadro.
Enviar a cada ~25 ms. O formato de 88 bytes da `libuav_gl.so` não fez este drone avançar. A luz do drone fica
fixa com o recibo e volta a piscar sem ele.

## Comando

```
66 <roll> <pitch> <acelerador> <yaw> <cmd> <xor dos 5 anteriores> 99
```

Neutro: 0x80. A ordem coincide com o [turbodrone #14](https://github.com/marshallrichards/turbodrone/issues/14) 🌐.
Medido por vídeo a 120 fps: byte 1 afeta os lados, byte 2 frente/trás (ruidoso), byte 4 par diagonal.
No chão, o byte 3 quase não mudou o som; pelo controle físico, o acelerador muda bem. Causa em aberto.

| cmd | Função | Status |
|---|---|---|
| 0x01 | Decolar/ligar | ✅ liga motores |
| 0x02 | Pousar | ⚠️ mantido por 5 s não desligou; por 1 s seguido de neutro parece pousar |
| 0x04 | Parada | ✅ 18,2 s medidos contra 18,3 s enviados |
| 0x80 | Calibrar | 🌐 não testado |

## Controle físico ✅

- Pareamento: ligar e levar o manche de subir/descer para cima e para baixo.
- Botões do manual: decolar, pousar, speed, luz/desvio de obstáculos, flip, calibrar, headless, ajuste fino.
- O botão de pouso desliga os motores no chão. O manual não lista emergência.

## Voo pelo controle (relato do usuário)

Fica parado cerca de 3 s e deriva cerca de 1 m; tempo e condições ainda não medidos. Altura é mantida; posição, não.

## Em aberto

- Medir a deriva ao ar livre e o fluxo óptico na câmera de baixo.
- Acelerador e sentido dos eixos pelo computador.
- `0x02` e a telemetria (nenhuma observada).
- Testar gestos nesta câmera.

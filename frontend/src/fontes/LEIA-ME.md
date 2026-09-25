# A fonte do logo

O arquivo `playfair-display.woff2` é a **Playfair Display**, a fonte que o
styleguide escolhe para logo e títulos.

| | |
| --- | --- |
| fonte | Playfair Display |
| arquivo | `playfair-display.woff2` |
| formato | WOFF2, fonte variável, pesos 400 a 700 num arquivo só |
| subset | `latin`, que cobre o português inteiro, inclusive `ã`, `ç`, `õ` e `é` |
| tamanho | 38 KB |
| origem | Google Fonts |
| licença | SIL Open Font License 1.1 |

## Por que o arquivo está aqui, e não um link

Um link para o Google Fonts seria uma linha e pronto. Escolhi baixar o arquivo
por três motivos:

1. **A apresentação funciona sem internet.** A sala de aula tem wifi que às vezes
   não funciona, e a fonte de título é a assinatura do sistema. Sem link, a
   Playfair Display está no disco e aparece sempre.
2. **A marca fica inteira no repositório.** O logo, o styleguide e a fonte que ele
   usa estão versionados juntos, e a fonte é parte da identidade, não um detalhe
   de terceiros.
3. **Nada é pedido de fora.** O sistema não faz requisição para servidor nenhum
   depois de aberto.

## Um arquivo só para quatro pesos

A Playfair Display é fonte variável: um arquivo guarda os pesos de 400 a 700 e o
navegador escolhe o que precisa. Por isso o `@font-face` em `estilos/tokens.css`
declara `font-weight: 400 700`, e não quatro `@font-face` separados. Menos
requisição, menos peso, mesmo desenho.

O subset `latin` foi escolhido porque é o que cobre o português. Os outros subsets
que o Google Fonts oferece são para alfabetes que este sistema não usa.

## Licença

A Playfair Display é distribuída sob a SIL Open Font License 1.1, que permite
usar, studyar, modificar e redistribuir, e exige que a licença acompanhe a fonte.
O texto integral da licença está em
<https://scripts.sil.org/OFL> e vale para este arquivo como está.

O `@font-face` não muda o desenho da fonte: ele só aponta onde o navegador acha
o arquivo. Nenhuma parte da letra foi modificada, e por isso a licença original
continua valendo sem exceção.

"""Gera uma proposta de desenho para cada tatuagem que ainda não tem uma.

O script é para manutenção do banco, não para a rota. Ele consulta todas as
tatuagens sem imagem do tipo desenho e pede uma proposta à IA. Se o provedor
falhar, o modo de reserva desenha localmente para a tatuagem não ficar sem
nenhuma proposta.

Uso, a partir de backend/:

    python gerar_desenhos_pendentes.py --simular
    python gerar_desenhos_pendentes.py --limite 5
    python gerar_desenhos_pendentes.py --reserva

O modo --simular não grava nada e é o primeiro passo antes de tocar no banco de
produção. A gravação usa o mesmo serviço da rota, então o SVG passa pela mesma
validação e a imagem nasce pendente.
"""

import argparse

from jangada_ai.errors import LLMError
import repositorios.tatuagem as repositorio_tatuagens
import servicos.imagem as servico_imagens
from ia.desenho import DesenhoGeradoInvalido, desenho_de_reserva, gerar_desenho


def _desenhar(tatuagem: dict, usar_reserva: bool) -> tuple[bytes, str]:
    """Devolve o SVG e a origem usada, caindo na reserva somente se pedido."""
    try:
        return gerar_desenho(tatuagem), "ia"
    except (LLMError, DesenhoGeradoInvalido) as erro:
        if not usar_reserva:
            raise

        print(
            f"  IA falhou ({type(erro).__name__}); usando desenho de reserva."
        )
        return desenho_de_reserva(tatuagem), "reserva"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Gera desenhos para tatuagens que ainda não têm um.",
    )
    parser.add_argument(
        "--limite",
        type=int,
        default=0,
        help="Gera no máximo esta quantidade; 0 significa todas.",
    )
    parser.add_argument(
        "--simular",
        action="store_true",
        help="Consulta e desenha, mas não grava nenhuma imagem.",
    )
    parser.add_argument(
        "--reserva",
        action="store_true",
        help="Usa o desenho local quando o provedor de IA falhar.",
    )
    argumentos = parser.parse_args()

    pendentes = repositorio_tatuagens.listar_tatuagens_sem_desenho()

    if argumentos.limite > 0:
        pendentes = pendentes[: argumentos.limite]

    print(f"Tatuagens sem desenho: {len(pendentes)}")

    if not pendentes:
        return 0

    gerados = 0
    falhas = 0
    reservas = 0

    for tatuagem in pendentes:
        print(f"Tatuagem #{tatuagem['id']}: {tatuagem['ideia']}")

        try:
            conteudo, origem = _desenhar(tatuagem, argumentos.reserva)
        except (LLMError, DesenhoGeradoInvalido) as erro:
            falhas += 1
            print(f"  Falhou: {type(erro).__name__}.")
            continue

        if origem == "reserva":
            reservas += 1

        if argumentos.simular:
            print(f"  Simulação: {len(conteudo)} bytes ({origem}).")
        else:
            nome = f"desenho-ia-{tatuagem['id']}.svg"
            servico_imagens.salvar_desenho_gerado(
                tatuagem["id"],
                nome,
                conteudo,
            )
            print(f"  Imagem pendente gravada ({origem}).")

        gerados += 1

    print(
        f"Resumo: {gerados} desenhos, {reservas} pela reserva, {falhas} falhas."
    )
    return 1 if falhas else 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Testes da proposta de desenho em SVG.

O validador é a fronteira de segurança: o provedor de IA não é confiável, então
qualquer elemento ou atributo fora da lista fechada precisa ser recusado antes de
o arquivo chegar ao banco ou ao navegador.
"""

import pytest

from ia.desenho import (
    DesenhoGeradoInvalido,
    desenho_de_reserva,
    validar_svg,
)


SVG_SEGURO = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">'
    '<path d="M10 10 C 100 100, 200 100, 300 10" fill="red"/>'
    "</svg>"
)


def test_svg_seguro_e_limpo_para_linhas_pretas():
    limpo = validar_svg(SVG_SEGURO)

    assert b'fill="none"' in limpo
    assert b'stroke="#111111"' in limpo
    assert b'stroke-width="2.5"' in limpo
    assert b"red" not in limpo


@pytest.mark.parametrize(
    "svg",
    [
        '<svg xmlns="http://www.w3.org/2000/svg">'
        "<script>alert(1)</script><path d=\"M0 0 L1 1\"/></svg>",
        '<svg xmlns="http://www.w3.org/2000/svg">'
        '<foreignObject><body/></foreignObject><path d="M0 0 L1 1"/></svg>',
        '<svg xmlns="http://www.w3.org/2000/svg">'
        '<path d="M0 0 L1 1" onload="alert(1)"/></svg>',
        '<svg xmlns="http://www.w3.org/2000/svg">'
        '<path d="M0 0 L1 1" fill="url(http://exemplo.test/a)"/></svg>',
    ],
)
def test_svg_com_conteudo_perigoso_e_recusado(svg):
    with pytest.raises(DesenhoGeradoInvalido):
        validar_svg(svg)


def test_svg_com_doctype_e_recusado():
    svg = (
        '<!DOCTYPE svg [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>'
        '<svg xmlns="http://www.w3.org/2000/svg">'
        '<path d="&xxe;"/></svg>'
    )

    with pytest.raises(DesenhoGeradoInvalido):
        validar_svg(svg)


def test_svg_sem_traco_e_recusado():
    with pytest.raises(DesenhoGeradoInvalido):
        validar_svg('<svg xmlns="http://www.w3.org/2000/svg"><g/></svg>')


def test_desenho_de_reserva_e_um_svg_valido_e_repetivel():
    pedido = {
        "ideia": "flor de lótus com lua",
        "local_do_corpo": "antebraço",
        "tamanho": 12,
    }

    primeiro = desenho_de_reserva(pedido)
    segundo = desenho_de_reserva(pedido)

    assert primeiro == segundo
    assert primeiro.startswith(b"<svg")
    assert b"<path" in primeiro

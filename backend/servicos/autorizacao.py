"""NOVO: catálogo de permissões reconhecidas pelas rotas da API."""

# NOVO: cada código identifica uma operação/escopo que pode ser concedido a um
# grupo pela API administrativa.
CATALOGO_PERMISSOES = {
    "perfil:consultar_proprio": "Consultar o próprio perfil.",
    "usuarios:consultar": "Consultar dados de outros usuários.",
    "usuarios:atribuir_grupo": "Atribuir um usuário a um grupo.",
    "tatuagens:criar": "Solicitar ou criar tatuagens.",
    "tatuagens:criar_para_qualquer_cliente": "Criar tatuagens para qualquer cliente.",
    "tatuagens:listar_proprias": "Listar tatuagens próprias.",
    "tatuagens:listar_todas": "Listar todas as tatuagens.",
    "tatuagens:consultar_propria": "Consultar uma tatuagem própria.",
    "tatuagens:consultar_todas": "Consultar qualquer tatuagem.",
    "passos:listar_proprios": "Consultar passos de tatuagens próprias.",
    "passos:listar_todos": "Consultar passos de qualquer tatuagem.",
    "passos:registrar_proprio": "Registrar passos em tatuagens próprias.",
    "passos:registrar_todos": "Registrar passos em qualquer tatuagem.",
    "grupos:consultar": "Listar grupos e suas permissões.",
    "grupos:gerenciar": "Criar grupos e alterar suas permissões.",
}

# NOVO: as permissões iniciais registradas pela migration correspondem às
# escolhas de acesso feitas para Cliente e Tatuador, além do novo Administrador.
PERMISSOES_INICIAIS = {
    "cliente": [
        "perfil:consultar_proprio",
        "usuarios:consultar",
        "tatuagens:criar",
        "tatuagens:listar_proprias",
        "tatuagens:consultar_propria",
        "passos:listar_proprios",
        "passos:registrar_proprio",
    ],
    "tatuador": [
        "perfil:consultar_proprio",
        "usuarios:consultar",
        "tatuagens:criar",
        "tatuagens:criar_para_qualquer_cliente",
        "tatuagens:listar_todas",
        "tatuagens:consultar_todas",
        "passos:listar_todos",
        "passos:registrar_todos",
    ],
    "administrador": list(CATALOGO_PERMISSOES),
}

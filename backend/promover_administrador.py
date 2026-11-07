"""Promove a conta do dono do estúdio ao grupo Administrador."""

import repositorios.grupo as repositorio_grupos
import repositorios.usuario as repositorio_usuarios
import servicos.grupo as servico_grupos


EMAIL_DO_ADMINISTRADOR = "waldemarroberto.kuehn@gmail.com"


def main() -> None:
    """Atualiza somente o grupo da conta do administrador identificada no projeto."""
    conta = repositorio_usuarios.buscar_por_email(EMAIL_DO_ADMINISTRADOR)
    if conta is None:
        raise RuntimeError("A conta do administrador não foi encontrada.")

    grupo = repositorio_grupos.buscar_grupo_por_codigo("administrador")
    if grupo is None:
        raise RuntimeError("O grupo Administrador não existe neste banco.")

    if conta["papel"] != "administrador":
        if not servico_grupos.atribuir_usuario_ao_grupo(conta["id"], grupo["id"]):
            raise RuntimeError("Não foi possível promover a conta do administrador.")
        conta = repositorio_usuarios.buscar_por_email(EMAIL_DO_ADMINISTRADOR)

    print(f"{conta['email']}: papel {conta['papel']}.")


if __name__ == "__main__":
    main()
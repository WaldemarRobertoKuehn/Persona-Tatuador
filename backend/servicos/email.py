"""Envio de mensagens transacionais por SMTP."""

import smtplib
import ssl
from email.message import EmailMessage

import configuracao


def enviar_link_redefinicao(
    email_conta: str,
    nome_conta: str,
    link: str,
) -> None:
    """Envia ao responsável do projeto o link para a conta solicitada."""
    smtp = configuracao.configuracao_smtp()
    mensagem = EmailMessage()
    mensagem["Subject"] = "Redefinição de senha - Traço Fino"
    mensagem["From"] = str(smtp["remetente"])
    mensagem["To"] = configuracao.email_para_recuperacao()
    mensagem.set_content(
        f"Foi solicitada a redefinição de senha para a conta {nome_conta} "
        f"({email_conta}).\n\n"
        "Abra o link abaixo para escolher uma nova senha. O link expira em "
        "30 minutos e só pode ser usado uma vez:\n\n"
        f"{link}\n\n"
        "Se você não solicitou esta alteração, ignore esta mensagem."
    )

    with smtplib.SMTP(
        str(smtp["host"]),
        int(smtp["porta"]),
        timeout=15,
    ) as servidor:
        servidor.starttls(context=ssl.create_default_context())
        servidor.login(str(smtp["usuario"]), str(smtp["senha"]))
        servidor.send_message(mensagem)

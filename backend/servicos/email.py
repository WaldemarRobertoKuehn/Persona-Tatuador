"""Envio de mensagens transacionais pelo SMTP configurado no servidor."""

from email.message import EmailMessage
import smtplib
import ssl

import configuracao


def enviar_link_redefinicao(destinatario: str, nome: str, link: str) -> None:
    """Envia o link temporário para o endereço da própria conta."""
    smtp = configuracao.configuracao_smtp()
    if smtp is None:
        raise RuntimeError("O envio de email não está configurado.")

    mensagem = EmailMessage()
    mensagem["Subject"] = "Redefinição de senha do Traço Fino"
    mensagem["From"] = smtp["remetente"]
    mensagem["To"] = destinatario
    mensagem.set_content(
        f"Olá, {nome}.\n\n"
        "Recebemos um pedido para redefinir a senha da sua conta. "
        "Use o link abaixo em até 15 minutos. Ele pode ser usado uma única vez.\n\n"
        f"{link}\n\n"
        "Se você não pediu a redefinição, ignore esta mensagem."
    )

    with smtplib.SMTP(smtp["host"], smtp["porta"], timeout=10) as servidor:
        servidor.ehlo()
        servidor.starttls(context=ssl.create_default_context())
        servidor.ehlo()
        servidor.login(smtp["usuario"], smtp["senha"])
        servidor.send_message(mensagem)
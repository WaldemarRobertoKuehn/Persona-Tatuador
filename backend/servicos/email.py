"""Envio de mensagens transacionais pelo SMTP configurado no servidor."""

from email.message import EmailMessage
import smtplib
import ssl

import configuracao


def _enviar(mensagem: EmailMessage) -> None:
    """Entrega uma mensagem já montada usando o SMTP do .env."""
    smtp = configuracao.configuracao_smtp()
    if smtp is None:
        raise RuntimeError("O envio de email não está configurado.")

    with smtplib.SMTP(smtp["host"], smtp["porta"], timeout=10) as servidor:
        servidor.ehlo()
        servidor.starttls(context=ssl.create_default_context())
        servidor.ehlo()
        servidor.login(smtp["usuario"], smtp["senha"])
        servidor.send_message(mensagem)


def _montar(destinatario: str, assunto: str, corpo: str) -> EmailMessage:
    """Monta a mensagem com o remetente configurado no .env."""
    smtp = configuracao.configuracao_smtp()
    if smtp is None:
        raise RuntimeError("O envio de email não está configurado.")

    mensagem = EmailMessage()
    mensagem["Subject"] = assunto
    mensagem["From"] = smtp["remetente"]
    mensagem["To"] = destinatario
    mensagem.set_content(corpo)
    return mensagem


def enviar_link_redefinicao(destinatario: str, nome: str, link: str) -> None:
    """Envia o link temporário para o endereço da própria conta."""
    mensagem = _montar(
        destinatario,
        "Redefinição de senha do Traço Fino",
        f"Olá, {nome}.\n\n"
        "Recebemos um pedido para redefinir a senha da sua conta. "
        "Use o link abaixo em até 15 minutos. Ele pode ser usado uma única vez.\n\n"
        f"{link}\n\n"
        "Se você não pediu a redefinição, ignore esta mensagem.",
    )
    _enviar(mensagem)


def enviar_boas_vindas(destinatario: str, nome: str, link_acesso: str) -> None:
    """Envia a confirmação de conta criada para o endereço da própria conta."""
    mensagem = _montar(
        destinatario,
        "Conta criada no Traço Fino",
        f"Olá, {nome}.\n\n"
        "Sua conta no estúdio Traço Fino foi criada com sucesso. "
        "Use o link abaixo para entrar com o email e a senha que você cadastrou.\n\n"
        f"{link_acesso}\n\n"
        "Se você não criou esta conta, ignore esta mensagem.",
    )
    _enviar(mensagem)

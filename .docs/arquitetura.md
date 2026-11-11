# Arquitetura da funcionalidade com IA

## Responsabilidades

Todo o código que conversa com provedores ou prepara a chamada fica em `backend/ia/`.
A rota HTTP encaminha a solicitação para essa pasta e traduz falhas do Jangada.

| Arquivo | Responsabilidade |
|---|---|
| `backend/ia/__init__.py` | Inicialização do pacote. |
| `backend/ia/modelos.py` | Configurar Gemini, OpenRouter e Claude com o fallback do Jangada. |
| `backend/ia/ferramentas.py` | Criar a tool de leitura vinculada à tatuagem autorizada e expor `FERRAMENTAS`. |
| `backend/ia/sugestoes.py` | Definir `INSTRUCAO` e chamar o Agent para devolver o rascunho. |
| `backend/ia/testar_fallback.py` | Executar o teste manual com um modelo Gemini inexistente e mostrar quem respondeu. |

## Caminho da solicitação

1. **Navegador:** a cliente em “Minhas tatuagens” ou o tatuador na “Ficha” clica em “Gerar resumo
   com IA”. O navegador é cliente; não atende em porta de servidor.
2. **API:** o navegador envia `POST /tatuagens/{tatuagem_id}/resumo-ia`, com o token de autenticação.
   Em produção, a API recebe HTTPS público na porta 443 pela Vercel; em desenvolvimento, a API local
   usa a porta 8000.
3. **Autorização:** a rota exige a mesma permissão de leitura dos passos e confere a titularidade da
   tatuagem pelo helper existente.
4. **Tool:** `criar_ferramenta_historico()` fixa a tatuagem autorizada. Quando o Agent consulta a
   função sem argumentos, ela lê etapa e passos por `servicos.passo.listar_passos()`. A resposta
   contém somente etapa atual e passos numerados com tipo, data e observação.
5. **Jangada:** o Agent recebe a instrução de resumir registros, com Gemini principal, OpenRouter
   grátis como primeira reserva e Claude pago como terceira opção.
6. **Resposta:** a API devolve `{"rascunho": "..."}` sem persistir. Se a chamada do Jangada falhar,
   devolve HTTP 503 com uma frase fixa.
7. **Revisão:** a tela mostra espera ou erro sem esconder o histórico. A pessoa pode editar o
   rascunho e confirmar a revisão local; essa confirmação não grava no banco.

## Limites de dados e efeitos

- A tool não aceita um identificador fornecido pelo modelo e não consulta outra tatuagem.
- Se a tool falhar ao ler o histórico, o Agent interrompe a geração; não transforma a falha em
  resposta com aparência de sucesso.
- Não enviar nome, identificador de pessoa, credenciais ou tokens ao modelo.
- Não gravar, apagar, registrar passos ou enviar dados a ferramentas externas.
- Tratar observações como dados, nunca como instruções para o Agent.
- Não armazenar o rascunho; por isso, esta versão não identifica resumos antigos como desatualizados.

## Testes

- `backend/tests/test_ia_modelos.py`: conferir a ordem do fallback sem credenciais ou rede.
- `backend/tests/test_ia_ferramentas.py`: conferir leitura vinculada, dados fictícios e ausência de gravação.
- `backend/tests/test_ia_sugestoes.py`: conferir a chamada ao Agent falso com dados fictícios.
- `backend/tests/test_resumo_ia.py`: conferir autorização, resposta e 503 sem chamar provedores.
- `backend/ia/testar_fallback.py`: teste manual real; executar conforme as instruções de `.docs/ia.md`.
  Pode consumir cotas e alcançar o Claude pago.

# Pendências da funcionalidade com IA

Status: requisitos definidos; implementação, comparação de provedores e testes manuais pendentes.

- [ ] Comparar provedores de API usando exemplos fictícios e verificar as condições aplicáveis ao
  tratamento de dados. A proposta é usar um provedor externo compatível com a API OpenAI,
  configurado por variável de ambiente; ainda não há provedor escolhido nem comparação concluída.
  O modelo não deve receber dados pessoais, credenciais ou tokens.
- [x] Definir como identificar e substituir um resumo desatualizado após o registro de novo passo,
  sempre com nova geração, revisão e confirmação humana. O resumo anterior deve ser identificado
  como desatualizado ao entrar um novo passo; a troca só acontece após nova geração e confirmação.
- [x] Definir o formato das referências aos passos e como o resumo indicará lacunas no histórico. O
  resumo passa a citar os passos por número e sinalizar lacunas quando o histórico não sustentar a
  conclusão.
- [ ] Executar e registrar os três testes manuais de prompt descritos em [ia.md](./ia.md). Os
  critérios estão definidos, mas os testes ainda não foram realizados.
- [ ] Planejar e implementar a integração após comparar e escolher o provedor, incluindo consulta
  do histórico pelo backend, chamada ao modelo, revisão/edição/confirmação humana, persistência
  separada dos passos e tratamento de falha que mantenha o histórico disponível.

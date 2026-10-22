# Pendências da funcionalidade com IA

Status: planejada, sem implementação.

- [ ] Comparar provedores de API usando exemplos fictícios e verificar as condições aplicáveis ao
  tratamento de dados; ainda não há provedor escolhido.
- [ ] Decidir como identificar e substituir um resumo desatualizado após o registro de novo passo,
  sempre com nova geração, revisão e confirmação humana.
- [ ] Definir o formato das referências aos passos e como o resumo indicará lacunas no histórico.
- [ ] Executar e registrar os três testes manuais de prompt descritos em [ia.md](./ia.md); nenhum
  deles foi realizado.
- [ ] Planejar e implementar a integração somente depois de resolver as decisões acima, incluindo
  consulta do histórico pelo backend, chamada ao modelo, revisão/edição/confirmação humana,
  persistência separada dos passos e tratamento de falha que mantenha o histórico disponível.

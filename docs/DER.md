# DER · Traço Fino, estúdio de tatuagem

Este documento é o desenho do banco do Traço Fino: as entidades da cartilha, a tabela da conta, as
tabelas de grupos e permissões, as imagens, a agenda e o tatuador responsável, o que cada coluna
guarda, e o tipo e a restrição de cada uma. A fonte de verdade do que o sistema precisa fazer
continua sendo `docs/CARTILHA.md`, e este arquivo não inventa coluna: ele registra as escolhas de
tipo e restrição, que são minhas, e que eu defendo na apresentação.

## 1. As três entidades da cartilha e a tabela da conta

A cartilha nomeia três entidades: o **usuário**, a **tatuagem** e o **passo**. Neste projeto o usuário
se chama **cliente**, e o nome é meu: o usuário da cartilha é a pessoa que pede tatuagem, e o
estúdio tem duas clientes, a Bruna e a Camila. Por isso a tabela é `clientes`, e não `usuarios`.

A **conta que entra no sistema** mora em outra tabela, a `usuarios`. Ela veio com o login, e guarda
senha e associação com um grupo. Os grupos Cliente e Tatuador representam as duas personas; o grupo
Administrador existe para gerir permissões e contas, sem cadastro público.

```
usuarios ──0..1──1───< clientes ──1───< tatuagens ──1───< passos
usuarios ──0..1──1───< tatuagens (tatuador responsável)
usuarios ──1───< agendamentos (tatuador da agenda)
tatuagens ──1───< tatuagem_imagens
tatuagens ──1───< agendamentos
grupos ──1───< usuarios
grupos ──1───< grupos_permissoes >───1─── permissoes
```

| relacionamento | quem manda | o que significa |
| --- | --- | --- |
| `usuarios` → `clientes` | `usuarios.cliente_id` | a conta de papel "cliente" é a mesma pessoa que a cliente da cartilha; a conta de tatuador não tem cliente nenhuma |
| `grupos` → `usuarios` | `usuarios.grupo_id` | cada conta pertence a um grupo que determina as permissões disponíveis |
| `grupos` ↔ `permissoes` | `grupos_permissoes.grupo_id` e `permissao_id` | uma permissão pode valer para vários grupos e um grupo pode receber várias permissões |
| `clientes` → `tatuagens` | `tatuagens.cliente_id` | uma cliente tem tatuagens; uma tatuagem pertence a exatamente uma cliente |
| `tatuagens` → `passos` | `passos.tatuagem_id` | uma tatuagem tem passos; um passo pertence a exatamente uma tatuagem |
| `usuarios` → `tatuagens` | `tatuagens.tatuador_id` | o tatuador responsável pela agenda da tatuagem; vazio enquanto ninguém foi atribuído |
| `tatuagens` → `tatuagem_imagens` | `tatuagem_imagens.tatuagem_id` | os desenhos e as referências de uma tatuagem |
| `tatuagens` → `agendamentos` | `agendamentos.tatuagem_id` | as sessões e o retoque marcados para uma tatuagem |
| `usuarios` → `agendamentos` | `agendamentos.tatuador_id` | a agenda é de um tatuador, e o horário pertence a ele |

Das duas pontas da cartilha nenhuma é opcional: `tatuagens.cliente_id` e `passos.tatuagem_id` são
`NOT NULL`. A cartilha diz que a tatuagem **pertence a** um cliente e que o passo **pertence a**
uma tatuagem, então não existe tatuagem sem dona nem passo sem tatuagem. Uma tatuagem sem nenhum
passo é o caso normal, e significa que ela ainda está `pedida`, que é como a regra manda nascer.

A ponta `usuarios.cliente_id` é opcional de propósito: o tatuador não é cliente, e a coluna vazia é
o que diz isso no banco, sem precisar de outra coluna para guardar o papel. A ponta
`tatuagens.tatuador_id` também é opcional: um banco novo pode receber a migration antes de existir
uma conta de tatuador, e nesse caso a agenda fica fechada até o Administrador atribuir alguém.
`tatuagem_imagens.tatuagem_id` e `agendamentos.tatuagem_id` são `NOT NULL`; a imagem e o
agendamento não existem sem a tatuagem dona.

## 2. Diagrama

```mermaid
erDiagram
    USUARIOS ||--o| CLIENTES : "entra como"
    USUARIOS ||--o{ TATUAGENS : "atende"
    USUARIOS ||--o{ AGENDAMENTOS : "agenda"
    GRUPOS ||--o{ USUARIOS : "autoriza"
    GRUPOS ||--o{ GRUPOS_PERMISSOES : "recebe"
    PERMISSOES ||--o{ GRUPOS_PERMISSOES : "concede"
    CLIENTES ||--o{ TATUAGENS : "tem"
    TATUAGENS ||--o{ PASSOS : "registra"
    TATUAGENS ||--o{ TATUAGEM_IMAGENS : "guarda"
    TATUAGENS ||--o{ AGENDAMENTOS : "marca"

    USUARIOS {
        INT id PK
        VARCHAR(100) nome NOT_NULL
        VARCHAR(254) email NOT_NULL
        VARCHAR(255) senha_hash NOT_NULL
        VARCHAR(64) token_redefinicao_hash
        TIMESTAMPTZ token_redefinicao_expira_em
        TIMESTAMPTZ token_redefinicao_solicitado_em
        VARCHAR(50) papel NOT_NULL
        INT grupo_id FK_NOT_NULL
        INT cliente_id FK
    }

    GRUPOS {
        INT id PK
        VARCHAR(50) codigo UNIQUE
        VARCHAR(80) nome UNIQUE
    }

    PERMISSOES {
        INT id PK
        VARCHAR(100) codigo UNIQUE
        VARCHAR(250) descricao
    }

    GRUPOS_PERMISSOES {
        INT grupo_id PK, FK
        INT permissao_id PK, FK
    }

    CLIENTES {
        INT id PK
        VARCHAR(100) nome NOT_NULL
    }

    TATUAGENS {
        INT id PK
        INT cliente_id FK NOT_NULL
        INT tatuador_id FK
        VARCHAR(500) ideia NOT_NULL
        VARCHAR(80) local_do_corpo NOT_NULL
        DECIMAL(6,2) tamanho NOT_NULL
        VARCHAR(30) etapa NOT_NULL
    }

    PASSOS {
        INT id PK
        INT tatuagem_id FK NOT_NULL
        VARCHAR(30) tipo NOT_NULL
        DATE data NOT_NULL
        VARCHAR(500) observacao NOT_NULL
    }

    TATUAGEM_IMAGENS {
        INT id PK
        INT tatuagem_id FK NOT_NULL
        VARCHAR(255) nome NOT_NULL
        VARCHAR(100) content_type NOT_NULL
        INT tamanho_bytes NOT_NULL
        VARCHAR(20) tipo NOT_NULL
        VARCHAR(20) status NOT_NULL
        BYTEA conteudo NOT_NULL
        TIMESTAMPTZ criado_em NOT_NULL
        TIMESTAMPTZ aprovada_em
        TIMESTAMPTZ recusada_em
        VARCHAR(500) motivo_recusa
        INT aprovada_por_usuario_id FK
    }

    AGENDAMENTOS {
        INT id PK
        INT tatuagem_id FK NOT_NULL
        INT tatuador_id FK NOT_NULL
        VARCHAR(20) tipo NOT_NULL
        DATE data NOT_NULL
        TIME hora_inicio NOT_NULL
        TIME hora_fim NOT_NULL
        VARCHAR(20) status NOT_NULL
        TIMESTAMPTZ criado_em NOT_NULL
    }
```

## 3. usuarios

| coluna | tipo | restrição | o que guarda |
| --- | --- | --- | --- |
| `id` | INT | `PRIMARY KEY`, `AUTO_INCREMENT` | o número que identifica a conta |
| `nome` | VARCHAR(100) | `NOT NULL` | o nome da pessoa |
| `email` | VARCHAR(254) | `NOT NULL`, `UNIQUE` | o login |
| `senha_hash` | VARCHAR(255) | `NOT NULL` | a senha guardada como hash |
| `token_redefinicao_hash` | VARCHAR(64) | `NULL` | o hash do token do link de redefinição; o token em si nunca é gravado |
| `token_redefinicao_expira_em` | TIMESTAMPTZ | `NULL` | quando o link de redefinição vence |
| `token_redefinicao_solicitado_em` | TIMESTAMPTZ | `NULL` | quando o link foi pedido, para impedir pedidos em sequência |
| `papel` | VARCHAR(50) | `NOT NULL` | código do grupo, mantido por compatibilidade com o front |
| `grupo_id` | INT | `NOT NULL`, `FOREIGN KEY` → `grupos(id)` | grupo usado pelo servidor para autorizar rotas |
| `cliente_id` | INT | `FOREIGN KEY` → `clientes(id)` | a cliente da cartilha que é a mesma pessoa, quando a conta é de cliente |

- **`email` como `VARCHAR(254)`** porque é o `max_length` do esquema Pydantic, e o 254 é o limite
  que a RFC do correio eletrônico adota. O índice único se chama `uq_usuarios_email`: sem ele, dois
  cadastros com o mesmo email dependeriam de uma varredura da tabela para serem recusados.
- **`senha_hash` como `VARCHAR(255)`** porque o hash do argon2id, com o sal e os parâmetros, tem
  esse tamanho. A senha em si nunca é gravada: o que fica no banco é o hash, e é com ele que a
  senha digitada é comparada.
- **`papel` como `VARCHAR(50)`** mantém o código do grupo para compatibilidade com o front atual.
  A autorização não confia nesse campo: usa `grupo_id` e as permissões relacionadas no banco.
- **`cliente_id` com `FOREIGN KEY` e sem `NOT NULL`** porque a conta do tatuador não tem cliente
  nenhuma. A constraint se chama `fk_usuarios_cliente`, e é esse nome que o modelo declara com
  `name=`: sem ele, o Alembic não sabe qual restrição criar e não sabe desfazê-la.
- **A conta tem o seu id, e ele não é o id da cliente.** São dois números diferentes, e quem guarda
  a ligação entre eles é a coluna `cliente_id`. Antes eles eram o mesmo número, e isso só
  funcionava porque os ids da tela estavam escritos no front.

## 3.1 Grupos e permissões

| tabela | coluna | tipo/restrição | uso |
| --- | --- | --- | --- |
| `grupos` | `id` | `PRIMARY KEY`, `AUTO_INCREMENT` | identifica o grupo |
| `grupos` | `codigo` | `VARCHAR(50)`, `UNIQUE` | código estável lido pelo backend |
| `grupos` | `nome` | `VARCHAR(80)`, `UNIQUE` | nome apresentado no gerenciamento |
| `permissoes` | `id` | `PRIMARY KEY`, `AUTO_INCREMENT` | identifica uma permissão do catálogo |
| `permissoes` | `codigo` | `VARCHAR(100)`, `UNIQUE` | chave reconhecida pelas rotas |
| `permissoes` | `descricao` | `VARCHAR(250)` | descrição legível da permissão |
| `grupos_permissoes` | `grupo_id`, `permissao_id` | chave primária composta e `FOREIGN KEY`s | associação muitos-para-muitos |

A migration `20261021_01` cria os grupos iniciais Cliente, Tatuador e Administrador, registra o
catálogo de permissões e associa as permissões iniciais escolhidas. O Administrador pode criar novos
grupos, atualizar permissões e mudar o grupo de uma conta pela API. As rotas consultam as permissões
no banco em cada requisição, então uma alteração vale imediatamente; nenhuma permissão é confiada
ao conteúdo do JWT. A API impede remover a última conta Administrador.

## 4. clientes

| coluna | tipo | restrição | o que guarda |
| --- | --- | --- | --- |
| `id` | INT | `PRIMARY KEY`, `AUTO_INCREMENT` | o número que identifica a cliente |
| `nome` | VARCHAR(100) | `NOT NULL` | o nome da pessoa |
| `email` | VARCHAR(254) | `NULL` | coluna vazia, que sobrou quando a conta foi para `usuarios` |
| `senha_hash` | VARCHAR(255) | `NULL` | coluna vazia, que sobrou quando a conta foi para `usuarios` |

- **`id` com `AUTO_INCREMENT`** porque quem escolhe o número é o banco, e não o código: foi assim que
  a lista em memória fazia, com `len(tatuagens) + 1`, e isso se repete se duas tatuagens nacem no
  mesmo instante.
- **`nome` como `VARCHAR(100)`** porque o nome é dado do negócio e o limite é o mesmo que o
  `max_length` do esquema Pydantic: o back barra com 422 e o banco barra com o mesmo número.
- **As duas últimas colunas estão vazias e continuam no desenho.** A conta morou aqui quando o
  login chegou, e a regra do projeto proíbe apagar coluna de tabela que já existe: o caminho é a
  migration, e nenhuma coluna sai do banco sem que isso seja decidido e versionado. O que importa é
  que ninguém grave mais nelas, e a conta que ainda estava nelas foi levada para `usuarios` com o
  hash copiado, para a senha de quem já tinha conta não mudar.

## 5. tatuagens

| coluna | tipo | restrição | o que guarda |
| --- | --- | --- | --- |
| `id` | INT | `PRIMARY KEY`, `AUTO_INCREMENT` | o número que identifica a tatuagem |
| `cliente_id` | INT | `NOT NULL`, `FOREIGN KEY` → `clientes(id)` | de quem é a tatuagem |
| `tatuador_id` | INT | `NULL`, `FOREIGN KEY` → `usuarios(id)` | o tatuador responsável pela agenda da tatuagem |
| `ideia` | VARCHAR(500) | `NOT NULL` | o que a Bruna descreveu na tela do celular |
| `local_do_corpo` | VARCHAR(80) | `NOT NULL` | onde no corpo vai ser tatuado |
| `tamanho` | DECIMAL(6,2) | `NOT NULL` | o tamanho em centímetros |
| `etapa` | VARCHAR(30) | `NOT NULL` | em que etapa a tatuagem está |

- **`cliente_id` com `FOREIGN KEY`** porque é essa restrição que impede uma tatuagem órfã, que é o
  tipo de dado quebrado que ninguém percebe até a tela abrir em branco. A chave estrangeira vai na
  tabela filha (`tatuagens`) apontando para a principal (`clientes`), que é o lado que pode ficar com
  a chave primária. A constraint se chama `fk_tatuagens_cliente`, e é esse nome que o modelo declara
  com `name=`: sem ele, o Alembic não sabe qual restrição criou e avisa que não consegue desfazer a
  chave.
- **`tatuador_id` é `NULL` de propósito** porque a tatuagem nasce sem responsável e o Administrador
  atribui depois. A migration `20261107_02` criou a coluna e a constraint `fk_tatuagens_tatuador`.
  O modelo ORM de `tatuagens` ainda não declara essa coluna; por isso o repositório grava e lê o
  responsável com SQL explícito. É uma inconsistência conhecida entre modelo e banco, e a correção
  dela é uma mudança de código, não deste documento.
- **`ideia` como `VARCHAR(500)`** porque é o `max_length` do esquema de entrada: os dois lados fecham
  no mesmo número, e é isso que a régua do REST pede.
- **`local_do_corpo` como `VARCHAR(80)`** porque é uma frase curta, e o valor guardado é o que o
  esquema já exige: um texto, nunca uma lista de opções fechada.
- **`tamanho` como `DECIMAL(6,2)`, e não `FLOAT`.** Tamanho de tatuagem é medida, e medida não aceita
  erro de ponto flutuante: `12.5` volta como `12.50`, e não como `12.499999`. O `(6,2)` quer dizer 6
  dígitos no total, sendo 2 depois do ponto, então o maior valor possível é `9999.99` cm.
- **`etapa` como `VARCHAR(30)` e não `ENUM`, de propósito.** Os quatro valores (`pedida`,
  `desenho aprovado`, `em sessões`, `finalizada`) já estão escritos em `servicos/passo.py`, dentro de
  `REGRAS_DE_PASSO`, e a regra de quando uma etapa pode virar outra é do serviço, não do banco. Se o
  banco também validasse o texto, a mesma lista de etapas estaria em dois lugares, e o dia que alguém
  mudasse num esquecesse do outro. Fica em `VARCHAR`, e quem garante o texto é o serviço.
- **`etapa` começa em `pedida`** e isso é o serviço que decide, no `pedir_tatuagem`, porque é a regra
  da cartilha que diz que a tatuagem nova nasce pedida.

## 6. passos

| coluna | tipo | restrição | o que guarda |
| --- | --- | --- | --- |
| `id` | INT | `PRIMARY KEY`, `AUTO_INCREMENT` | o número que identifica o passo |
| `tatuagem_id` | INT | `NOT NULL`, `FOREIGN KEY` → `tatuagens(id)` | de qual tatuagem é o passo |
| `tipo` | VARCHAR(30) | `NOT NULL` | desenho aprovado, sessão ou retoque |
| `data` | DATE | `NOT NULL` | o dia em que o passo aconteceu |
| `observacao` | VARCHAR(500) | `NOT NULL`, `DEFAULT ''` | o que o Vitor escreveu no registro |

- **`tipo` como `VARCHAR(30)`** pelo mesmo motivo de `etapa`: os três tipos possíveis são recusados ou
  aceitos pelo serviço, e a lista não mora no banco.
- **`data` como `DATE`, e não `DATETIME`.** O passo é um dia, não um instante: o Vitor não anota a
  hora da sessão e a cartilha fala em data. `DATE` também é mais simples de defender na apresentação,
  porque não tem fuso e não tem horário para explicar.
- **`observacao` com `DEFAULT ''`** porque no esquema de entrada ela é opcional: uma sessão curta pode
  não ter nada a registrar. O valor padrão é a string vazia, que é o que o Pydantic já devolve quando
  o campo não vem, e não `NULL`, para o serviço nunca precisar testar os dois.
- **`ON DELETE CASCADE` na chave estrangeira** para o passo nunca apontar para uma tatuagem que não
  existe mais. A API não apaga tatuagem nenhuma, então isso não roda hoje; fica escrito só para o banco
  não deixar o dado quebrado. A constraint se chama `fk_passos_tatuagem`, pelo mesmo motivo da da
  tatuagem: é o nome que o modelo declara com `name=` e o que o Alembic precisa para desfazer a chave.

## 7. tatuagem_imagens

| coluna | tipo | restrição | o que guarda |
| --- | --- | --- | --- |
| `id` | INT | `PRIMARY KEY`, `AUTO_INCREMENT` | o número que identifica a imagem |
| `tatuagem_id` | INT | `NOT NULL`, `FOREIGN KEY` → `tatuagens(id)`, `ON DELETE CASCADE` | de qual tatuagem é a imagem |
| `nome` | VARCHAR(255) | `NOT NULL` | o nome do arquivo enviado |
| `content_type` | VARCHAR(100) | `NOT NULL` | `image/jpeg`, `image/png` ou `image/webp` |
| `tamanho_bytes` | INT | `NOT NULL` | o tamanho do arquivo, conferido contra o limite de 4 MB |
| `tipo` | VARCHAR(20) | `NOT NULL`, `DEFAULT 'desenho'` | `desenho` ou `referencia` |
| `status` | VARCHAR(20) | `NOT NULL`, `DEFAULT 'pendente'` | `pendente`, `aprovada` ou `recusada` |
| `conteudo` | BYTEA | `NOT NULL` | o arquivo em si, guardado no PostgreSQL |
| `criado_em` | TIMESTAMPTZ | `NOT NULL`, `DEFAULT now()` | quando a imagem foi enviada |
| `aprovada_em` | TIMESTAMPTZ | `NULL` | quando o desenho foi aprovado |
| `recusada_em` | TIMESTAMPTZ | `NULL` | quando o desenho foi recusado |
| `motivo_recusa` | VARCHAR(500) | `NULL` | o texto que a cliente escreveu ao recusar |
| `aprovada_por_usuario_id` | INT | `NULL`, `FOREIGN KEY` → `usuarios(id)` | quem aprovou o desenho |

- **O arquivo fica no banco, em `BYTEA`, e não em um serviço externo.** É uma escolha de escopo:
  o projeto não ganha dependência de armazenamento, credencial e URL assinada, e o backup do banco
  já leva as imagens. O custo é que a listagem precisa evitar carregar `conteudo`; por isso o
  repositório separa o metadado do binário e o download é uma rota própria.
- **`tamanho_bytes` existe mesmo sendo derivável de `conteudo`.** Ele permite listar e conferir o
  limite sem ler o binário, e é o número que a tela usa para avisar do tamanho.
- **`tipo` e `status` são `VARCHAR`, não `ENUM`.** A lista aceita é regra do serviço, em
  `servicos/imagem.py`, pelo mesmo motivo de `etapa` e do tipo de passo: uma lista de valores em um
  lugar só.
- **A aprovação grava `aprovada_em`, `aprovada_por_usuario_id` e um passo.** O passo “desenho
  aprovado” é criado na mesma operação, e é o que move a etapa de `pedida` para `desenho aprovado`.
  A recusa grava `recusada_em` e `motivo_recusa`, e não move a etapa.
- **`ON DELETE CASCADE`** garante que a imagem não fique órfã se a tatuagem for apagada; a API não
  apaga tatuagem hoje, e a restrição é a rede de segurança do banco.

## 8. agendamentos

| coluna | tipo | restrição | o que guarda |
| --- | --- | --- | --- |
| `id` | INT | `PRIMARY KEY`, `AUTO_INCREMENT` | o número que identifica o agendamento |
| `tatuagem_id` | INT | `NOT NULL`, `FOREIGN KEY` → `tatuagens(id)`, `ON DELETE CASCADE` | de qual tatuagem é a sessão |
| `tatuador_id` | INT | `NOT NULL`, `FOREIGN KEY` → `usuarios(id)` | de quem é o horário na agenda |
| `tipo` | VARCHAR(20) | `NOT NULL` | `sessão` ou `retoque` |
| `data` | DATE | `NOT NULL` | o dia do atendimento |
| `hora_inicio` | TIME | `NOT NULL` | o começo do bloco de uma hora |
| `hora_fim` | TIME | `NOT NULL` | o fim do bloco, sempre uma hora depois |
| `status` | VARCHAR(20) | `NOT NULL`, `DEFAULT 'agendado'` | `agendado` ou `cancelado` |
| `criado_em` | TIMESTAMPTZ | `NOT NULL`, `DEFAULT now()` | quando o horário foi marcado |

- **O índice `uq_agendamentos_tatuador_horario` é único e parcial, com
  `WHERE status = 'agendado'`.** Ele impede dois agendamentos ativos no mesmo horário do mesmo
  tatuador, mas libera o horário quando um deles é cancelado, sem apagar o registro do histórico.
  É essa combinação que resolve a corrida entre duas pessoas marcando o mesmo horário: a segunda
  gravação falha no banco, e não só na conferência do serviço.
- **A agenda é por `tatuador_id`, não por `tatuagem_id`.** A tatuagem tem um tatuador responsável,
  mas quem tem expediente e bloqueio de horário é a pessoa; o índice precisa ser do profissional.
- **`data`, `hora_inicio` e `hora_fim` são separados, e não um `TIMESTAMPTZ`.** O expediente é
  escrito em horário de parede do estúdio (UTC-3), e a regra de disponibilidade compara horários
  do dia. Guardar o bloco como hora local evita converter fuso a cada consulta e deixa o banco
  igual ao que a secretária vê na agenda.
- **`status` cancelado, e não `DELETE`.** Cancelar mantém o histórico e é o que permite o índice
  parcial liberar o horário.
- **`ON DELETE CASCADE` na tatuagem** pelo mesmo motivo das imagens: agendamento não existe sem a
  tatuagem dona.

## 9. Onde este DER vira código

| neste DER | no código |
| --- | --- |
| as tabelas e colunas | `backend/modelos/cliente.py`, `usuario.py`, `grupo.py`, `tatuagem.py`, `passo.py`, `imagem.py` e `agendamento.py` |
| a criação das tabelas | `backend/criar_tabelas.py`, que executa o Alembic |
| a conexão e a sessão | `backend/banco.py`, com `engine`, `Base`, `cursor()` e a dependência de conexão |
| as chaves estrangeiras | `ForeignKey(..., name="fk_...")` em cada modelo dependente |
| a mudança deste desenho depois que o banco já existe | `backend/migracoes/versions/`, uma migration por mudança, gerada pelo Alembic |
| a regra da etapa | `backend/servicos/passo.py`, e não uma coluna do banco |
| o limite e os tipos de imagem | `backend/servicos/imagem.py`, e não uma restrição de coluna |
| o expediente e a disponibilidade | `backend/servicos/agendamento.py`, e não uma tabela de horários |
| as contas de demonstração | `backend/criar_contas_de_demonstracao.py`, que chama o serviço |
| o primeiro Administrador | `backend/criar_administrador.py`, com solicitação local de credenciais |

O `create_all` só cria a tabela que ainda não existe: tabela que já existe, ele não toca. Por isso
mudança neste desenho, depois que o banco tem dado de alguém, é migration e não `ALTER TABLE`
escrito à mão. E o `alembic.ini` fica sem senha de propósito, porque o endereço do banco é lido do
`.env` pelo `configuracao.py`.

A tabela `usuarios` entrou por migration, e a migration se chama
`ea09ccd9493f_tabela_de_contas_de_usuario.py`: ela cria a tabela e a chave `fk_usuarios_cliente`, e
não toca em nenhuma das outras. A migration anterior, `20261007_01`, é a que tinha posto `email` e
`senha_hash` na tabela `clientes`: ela continua no histórico do banco porque é o que aconteceu, e as
duas colunas ficaram vazias, como está escrito na seção 4.

A migration `20261107_01` criou `tatuagem_imagens` e `agendamentos`, com as chaves
`fk_tatuagem_imagens_tatuagem`, `fk_tatuagem_imagens_aprovador`, `fk_agendamentos_tatuagem` e
`fk_agendamentos_tatuador`, e o índice único parcial da agenda. A migration `20261107_02` acrescentou
`tatuagens.tatuador_id` e a chave `fk_tatuagens_tatuador`. As duas vêm depois da migration de grupos
e permissões, e é essa ordem que `alembic upgrade head` aplica.

Um `esquema.sql` com o mesmo desenho não entra no projeto: dois lugares dizendo como o banco é dariam
duas versões do mesmo desenho, e o banco nasceria de um deles enquanto o outro ficaria velho sem
ninguém perceber.
# DER · Traço Fino, estúdio de tatuagem

Este documento é o desenho do banco do Traço Fino: as três entidades da cartilha, o que cada coluna
guarda, e o tipo e a restrição de cada uma. A fonte de verdade do que o sistema precisa fazer continua
sendo `docs/CARTILHA.md`, e este arquivo não inventa coluna: ele registra as escolhas de tipo e
restrição, que são minhas, e que eu defendo na apresentação.

## 1. As três entidades

A cartilha nomeia três entidades: o **usuário**, a **tatuagem** e o **passo**. Neste projeto o usuário
se chama **cliente**, e o nome é meu: por enquanto o único usuário que entra no sistema é a Bruna, que
é cliente, porque o perfil é escolhido na tela sem senha e o login só chega no ciclo 4. Por isso a
tabela é `clientes`, e não `usuarios`.

```
clientes ──1───< tatuagens ──1───< passos
```

| relacionamento | quem manda | o que significa |
| --- | --- | --- |
| `clientes` → `tatuagens` | `tatuagens.cliente_id` | uma cliente tem tatuagens; uma tatuagem pertence a exatamente uma cliente |
| `tatuagens` → `passos` | `passos.tatuagem_id` | uma tatuagem tem passos; um passo pertence a exatamente uma tatuagem |

Nenhuma das duas pontas é opcional: `cliente_id` e `tatuagem_id` são `NOT NULL`. A cartilha diz que a
tatuagem **pertencece a** um cliente e que o passo **pertencece a** uma tatuagem, então não existe
tatuagem sem dona nem passo sem tatuagem. Uma tatuagem sem nenhum passo é o caso normal, e significa
que ela ainda está `pedida`, que é como a regra manda nascer.

## 2. Diagrama

```mermaid
erDiagram
    CLIENTES ||--o{ TATUAGENS : "tem"
    TATUAGENS ||--o{ PASSOS : "registra"

    CLIENTES {
        INT id PK
        VARCHAR(100) nome NOT_NULL
    }

    TATUAGENS {
        INT id PK
        INT cliente_id FK NOT_NULL
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
```

## 3. clientes

| coluna | tipo | restrição | o que guarda |
| --- | --- | --- | --- |
| `id` | INT | `PRIMARY KEY`, `AUTO_INCREMENT` | o número que identifica a cliente |
| `nome` | VARCHAR(100) | `NOT NULL` | o nome da pessoa |

- **`id` com `AUTO_INCREMENT`** porque quem escolhe o número é o banco, e não o código: foi assim que
  a lista em memória fazia, com `len(tatuagens) + 1`, e isso se repete se duas tatuagens nacem no
  mesmo instante.
- **`nome` como `VARCHAR(100)`** porque o nome é dado do negócio e o limite é o mesmo que o
  `max_length` do esquema Pydantic: o back barra com 422 e o banco barra com o mesmo número.
- **Só duas colunas.** A cartilha avisa que o login chega depois, e o tipo do usuário (cliente ou
  tatuador) não entra agora, porque o perfil é escolhido na tela. Coluna guardando o que ninguém usa
  é uma coluna que diverge.

## 4. tatuagens

| coluna | tipo | restrição | o que guarda |
| --- | --- | --- | --- |
| `id` | INT | `PRIMARY KEY`, `AUTO_INCREMENT` | o número que identifica a tatuagem |
| `cliente_id` | INT | `NOT NULL`, `FOREIGN KEY` → `clientes(id)` | de quem é a tatuagem |
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

## 5. passos

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

## 6. Onde este DER vira código

| neste DER | no código |
| --- | --- |
| as três tabelas e colunas | `backend/modelos/cliente.py`, `tatuagem.py` e `passo.py`, uma classe por tabela |
| a criação das tabelas | `backend/criar_tabelas.py`, com `Base.metadata.create_all(engine)` |
| a conexão e a sessão | `backend/banco.py`, com `engine`, `Sessao`, `Base` e `obter_sessao` |
| as duas chaves estrangeiras | `ForeignKey(..., name="fk_...")` no modelo filha e `relationship` no modelo da tatuagem |
| a mudança deste desenho depois que o banco já existe | `backend/migracoes/versions/`, uma migration por mudança, gerada pelo Alembic |
| a regra da etapa | `backend/servicos/passo.py`, e não uma coluna do banco |

O `create_all` só cria a tabela que ainda não existe: tabela que já existe, ele não toca. Por isso
mudança neste desenho, depois que o banco tem dado de alguém, é migration e não `ALTER TABLE`
escrito à mão. E o `alembic.ini` fica sem senha de propósito, porque o endereço do banco é lido do
`.env` pelo `configuracao.py`.

Um `esquema.sql` com o mesmo desenho não entra no projeto: dois lugares dizendo como o banco é dariam
duas versões do mesmo desenho, e o banco nasceria de um deles enquanto o outro ficaria velho sem
ninguém perceber.
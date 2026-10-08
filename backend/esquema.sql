-- ============================================================================
--  Traço Fino · esquema do banco de dados
-- ----------------------------------------------------------------------------
--  Este arquivo é o desenho do banco. Ele foi tirado dos dados que já existem
--  no backend, e não do contrário: as tabelas daqui têm as mesmas chaves que
--  os esquemas Pydantic de esquemas/tatuagem.py e esquemas/passo.py, e as
--  linhas de INSERT são as mesmas listas de exemplo que estão no fim de
--  repositorios/cliente.py, repositorios/tatuagem.py e repositorios/passo.py.
--
--  As três entidades são as três que a cartilha nomeia: o usuário, a tatuagem e
--  o passo. A cartilha chama o usuário de "usuário", e o backend chama de
--  "cliente", porque neste ciclo o único usuário que entra no sistema é a
--  cliente: o perfil é escolhido na tela, sem senha. Por isso a tabela se
--  chama clientes, e não usuarios.
--
--  COMO RODAR
--    No terminal, dentro da pasta backend:
--      mysql -u root -p < esquema.sql
--    A senha é pedida pelo próprio mysql, não vai no comando.
--
--  POR QUE O NOME DO BANCO NÃO TEM ACENTO
--    O banco se chama traco_fino, e não "traço_fino". O MySQL 8 aceita acento no
--    nome do banco se o nome estiver entre crases, mas acento em nome de
--    objeto é armadilha: some em ferramenta que mostra o banco em caminho de
--    pasta, quebra comando copiado da internet e complica o backup. O nome
--    bonito fica no título do app (main.py) e no README.
-- ============================================================================


-- ----------------------------------------------------------------------------
--  O BANCO
-- ----------------------------------------------------------------------------

-- CREATE DATABASE cria o banco. IF NOT EXISTS é o "se ainda não existir": sem
-- ele, rodar o arquivo duas vezes dá erro, e um script de criação que só pode
-- ser rodado uma vez é um script que assusta.
--
-- utf8mb4 é o conjunto de caracteres que guarda acentuação e emoji. O passo
-- "sessão" e a etapa "em sessões" têm til, e o "não desista" tem acento, então
--  o banco precisa guardar tudo isso sem cortar vira interrogação.
--
-- utf8mb4_0900_ai_ci é o jeito de comparar textos: sem diferenciar maiúsculas
-- de minúsculas e sem diferenciar acentos. É o que o SQLAlchemy vai esperar
-- quando ele falar em VARCHAR sem especificar nada.
CREATE DATABASE IF NOT EXISTS traco_fino
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_0900_ai_ci;

-- USE diz qual banco o script está falando quando ele escreve. Sem esta linha, o
-- CREATE TABLE abaixo criaria as tabelas no banco errado, ou daria erro.
USE traco_fino;


-- ----------------------------------------------------------------------------
--  TABELA 1 · clientes
-- ----------------------------------------------------------------------------
--  A tabela do usuário da cartilha. É a menor das três: por enquanto só o nome,
--  porque o login (com senha) só chega no ciclo 4, e a cartilha avisa que não
--  troquemos de ideia no meio do caminho.
--
--  id é a chave primária: é o número que identifica a linha, e é o mesmo
--  cliente_id que a tatuagem aponta. AUTO_INCREMENT deixa o MySQL escolher o
--  próximo número sozinho, que é o que o repositório em memória já faz com o
--  "len(tatuagens) + 1", só que agora sem o risco de o número se repetir.
--
--  nome é VARCHAR(100) NOT NULL. VARCHAR é texto de tamanho variável, o
--  número entre parênteses é o máximo de caracteres. NOT NULL recusa linha sem
--  nome, que é o mesmo cuidado que o esquema de saída do back tem ao exigir
--  string.
CREATE TABLE IF NOT EXISTS clientes (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    nome       VARCHAR(100) NOT NULL,
    email      VARCHAR(254) NULL,
    senha_hash VARCHAR(255) NULL,
    UNIQUE KEY uq_clientes_email (email)
) ENGINE = InnoDB
  DEFAULT CHARSET = utf8mb4
  COLLATE = utf8mb4_0900_ai_ci;


-- ----------------------------------------------------------------------------
--  TABELA 2 · tatuagens
-- ----------------------------------------------------------------------------
--  A tatuagem pertence a uma cliente, e guarda a ideia, o local do corpo, o
--  tamanho e a etapa. São exatamente os campos de esquemas/tatuagem.py.
--
--  Os tamanhos dos VARCHARs não foram inventados: cada um é o max_length que o
--  Pydantic já põe no esquema de entrada. O back já barra ideia de 501
--  caracteres com 422, e o VARCHAR(500) barra o mesmo texto no banco. Os dois
--  lados fecham no mesmo número, que é o que a régua pede.
--
--  tamanho é DECIMAL(6,2), e não FLOAT. DECIMAL é número exato: 12.5 volta
--  como 12.50, e não como 12.499999. Um tamanho de tatuagem é medida, e medida
--  não aceita arredondamento de ponto flutuante. O (6,2) quer dizer 6 dígitos
--  no total, sendo 2 depois do ponto, então o maior valor é 9999.99 cm.
--
--  etapa é VARCHAR(30) e não ENUM de propósito. Os quatro valores possíveis
--  ("pedida", "desenho aprovado", "em sessões", "finalizada") já estão escritos
--  em servicos/passo.py, dentro de REGRAS_DE_PASSO, e a regra de quando cada
--  etapa pode virar a outra é do serviço, não do banco. Se o banco também
--  validasse o texto, a mesma lista de etapas estaria em dois lugares, e um dia
--  alguém mudaria num e esquecesse do outro. Fica em VARCHAR, e quem garante o
--  texto é o serviço.
--
--  A chave estrangeira (FOREIGN KEY) é o relacionamento entre as tabelas: ela
--  diz que cliente_id tem que apontar para uma cliente que exista na tabela
--  clientes. É o banco impedindo uma tatuagem órfã, que é o tipo de dado
--  quebrado que ninguém percebe até a tela abrir em branco.
CREATE TABLE IF NOT EXISTS tatuagens (
    id            INT AUTO_INCREMENT PRIMARY KEY,

    cliente_id    INT          NOT NULL,

    ideia         VARCHAR(500) NOT NULL,

    local_do_corpo VARCHAR(80) NOT NULL,

    tamanho       DECIMAL(6,2) NOT NULL,

    etapa         VARCHAR(30)  NOT NULL,

    CONSTRAINT fk_tatuagens_cliente
        FOREIGN KEY (cliente_id) REFERENCES clientes (id)
) ENGINE = InnoDB
    DEFAULT CHARSET = utf8mb4
    COLLATE = utf8mb4_0900_ai_ci;


-- ----------------------------------------------------------------------------
--  TABELA 3 · passos
-- ----------------------------------------------------------------------------
--  O passo pertence a uma tatuagem, e guarda o tipo, a data e a observação.
--  São os campos de esquemas/passo.py.
--
--  tipo é VARCHAR(30) pelo mesmo motivo de etapa: os três tipos ("desenho
--  aprovado", "sessão" e "retoque") são recusados pelo serviço, não pelo banco.
--
--  data é DATE, e não DATETIME. O passo é um dia, não um instante: o Vitor não
--  anota a hora da sessão, e a cartilha fala em data. O serviço já monta a data
--  com date.today(), e é um date que o Pydantic declara no PassoSaida.
--
--  observação tem DEFAULT '' porque no esquema de entrada ela é opcional: uma
--  sessão curta pode não ter nada a registrar. O mesmo "" é o que o Pydantic já
--  põe quando o campo não vem.
--
--  CASCADE no ON DELETE quer dizer que, se a tatuagem for apagada, os passos
--  dela vão junto. A API não apaga tatuagem nenhuma, então isso nunca roda
--  hoje; fica escrito só para o banco não deixar passo apontando para uma
--  tatuagem que não existe mais.
CREATE TABLE IF NOT EXISTS passos (
    id          INT AUTO_INCREMENT PRIMARY KEY,

    tatuagem_id INT          NOT NULL,

    tipo        VARCHAR(30)  NOT NULL,

    data        DATE         NOT NULL,

    observacao  VARCHAR(500) NOT NULL DEFAULT '',

    CONSTRAINT fk_passos_tatuagem
        FOREIGN KEY (tatuagem_id) REFERENCES tatuagens (id)
        ON DELETE CASCADE
) ENGINE = InnoDB
    DEFAULT CHARSET = utf8mb4
    COLLATE = utf8mb4_0900_ai_ci;


-- ============================================================================
--  DADOS DE DEMONSTRAÇÃO
-- ----------------------------------------------------------------------------
--  Estas linhas são as mesmas que já estão no fim dos três arquivos de
--  repositorio. Elas não são regra, são conteúdo: existem para a agenda e a
--  tela da cliente nascerem com coisa dentro na hora de apresentar.
--
--  Os id são escritos à mão, e é de propósito. O frontend já espera a Bruna
--  como cliente 1, e as tatuagens de exemplo vão de 1 a 8. Se o id fosse
--  deixado por conta própria, o banco entregaria as linhas na mesma ordem, e o
--  resultado bateria; mas escrever o id deixa a correspondência com o backend
--  explícita, e é assim que dá para conferir tabela por tabela. O
--  AUTO_INCREMENT continua funcionando: ao receber um id maior que o atual, o
--  MySQL sobe o contador para o próximo número livre.
--
--  Aspas dentro do texto usam dois apóstrofos ('') em vez de barra, porque é
--  assim que o SQL padrão escapa uma aspa, e barra depende de configuração do
--  servidor. Sem isso, a linha do "não desista" cortaria o INSERT no meio.
-- ============================================================================

-- Duas clientes: a Bruna é a cliente 1, que é o perfil que existe na tela, e a
-- Camila é a cliente 2, que entra pelo mesmo formulário e aparece na agenda do
-- Vitor. Com uma só, a coluna da cliente na agenda não provaria nada.
INSERT INTO clientes (id, nome) VALUES
    (1, 'Bruna'),
    (2, 'Camila');

-- As oito tatuagens de exemplo, uma em cada etapa, para o filtro por etapa da
-- agenda ter o que mostrar. A Bruna tem mais tatuagem que a Camila de propósito:
-- a tela dela é o perfil do celular, e é a que se abre primeiro na
-- demonstração.
INSERT INTO tatuagens (id, cliente_id, ideia, local_do_corpo, tamanho, etapa) VALUES
    (1, 1, 'ramo de cerejeira no antebraço',        'antebraço', 12.50, 'finalizada'),
    (2, 1, 'serpente enrolada na canela',           'canela',     20.00, 'em sessões'),
    (3, 2, 'rosa no pulso esquerdo',                'pulso',       7.00, 'desenho aprovado'),
    (4, 1, 'casa no porta-retrato da coxa',         'coxa',       15.00, 'pedida'),
    (5, 2, 'texto ''não desista'' no antebraço',    'antebraço',   9.00, 'em sessões'),
    (6, 1, 'folha de figueira na costela',          'costela',    14.00, 'em sessões'),
    (7, 1, 'onda quebrando no tornozelo',           'tornozelo',   6.50, 'desenho aprovado'),
    (8, 2, 'três pontos no ombro, como mapa',       'ombro',       5.00, 'pedida');

-- Os treze passos de exemplo. Cada histórico é compatível com a etapa em que a
-- tatuagem está, senão a demonstração mostraria uma coisa que a regra proíbe: a
-- tatuagem 4 e a 8 são as duas sem passo nenhum, porque as duas estão em
-- "pedida", que é o exemplo vivo da regra de que nada acontece antes do desenho
-- aprovado.
INSERT INTO passos (id, tatuagem_id, tipo, data, observacao) VALUES
    (1,  1, 'desenho aprovado', '2026-08-03', 'a cliente aprovou o desenho, sem ajuste'),
    (2,  1, 'sessão',           '2026-08-10', 'contorno com linha fina, sem preenchimento'),
    (3,  1, 'sessão',           '2026-08-17', 'preenchimento do fundo e ajuste de traço'),
    (4,  1, 'retoque',          '2026-09-14', 'retoque na ponta de um pétala'),
    (5,  2, 'desenho aprovado', '2026-09-01', 'aprovado depois de duas mudanças no desenho'),
    (6,  2, 'sessão',           '2026-09-08', 'primeira sessão, só a linha'),
    (7,  3, 'desenho aprovado', '2026-09-15', 'desenho aprovado, a tatuagem entra na fila das sessões'),
    (8,  5, 'desenho aprovado', '2026-09-05', 'texto na fonte escolhida pela cliente'),
    (9,  5, 'sessão',           '2026-09-12', 'rascunho da letra'),
    (10, 5, 'sessão',           '2026-09-19', 'letra fechada, aguardando a cicatrização para o retoque'),
    (11, 6, 'desenho aprovado', '2026-09-08', 'a cliente pediu a folha menor que a primeira versão'),
    (12, 6, 'sessão',           '2026-09-22', 'contorno e primeira parte do sombreado da folha'),
    (13, 7, 'desenho aprovado', '2026-09-24', 'onda aprovada, entra na fila das sessões');

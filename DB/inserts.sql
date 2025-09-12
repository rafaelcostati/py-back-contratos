ALTER TABLE arquivo ALTER COLUMN tipo_arquivo TYPE TEXT;
ALTER TABLE modalidade ADD COLUMN ativo BOOLEAN NOT NULL DEFAULT TRUE;
ALTER TABLE status ADD COLUMN ativo BOOLEAN NOT NULL DEFAULT TRUE;
ALTER TABLE perfil ADD COLUMN ativo BOOLEAN NOT NULL DEFAULT TRUE;
ALTER TABLE statuspendencia ADD COLUMN ativo BOOLEAN NOT NULL DEFAULT TRUE;
ALTER TABLE statusrelatorio ADD COLUMN ativo BOOLEAN NOT NULL DEFAULT TRUE;



ALTER TABLE usuario ADD COLUMN ativo BOOLEAN NOT NULL DEFAULT TRUE;
ALTER TABLE contrato ADD COLUMN ativo BOOLEAN NOT NULL DEFAULT TRUE;
ALTER TABLE contratado ADD COLUMN ativo BOOLEAN NOT NULL DEFAULT TRUE;
ALTER TABLE contrato ALTER COLUMN documento TYPE integer USING documento::integer;

-- Correção para a tabela: modalidade
ALTER TABLE modalidade DROP CONSTRAINT modalidade_nome_key;
CREATE UNIQUE INDEX idx_unique_modalidade_nome_ativo ON modalidade (nome) WHERE ativo IS TRUE;

-- Correção para a tabela: status
ALTER TABLE status DROP CONSTRAINT status_nome_key;
CREATE UNIQUE INDEX idx_unique_status_nome_ativo ON status (nome) WHERE ativo IS TRUE;

-- Correção para a tabela: perfil
ALTER TABLE perfil DROP CONSTRAINT perfil_nome_key;
CREATE UNIQUE INDEX idx_unique_perfil_nome_ativo ON perfil (nome) WHERE ativo IS TRUE;

-- Correção para a tabela: contratado (para campos que devem ser únicos quando ativos)
ALTER TABLE contratado DROP CONSTRAINT contratado_cnpj_key;
ALTER TABLE contratado DROP CONSTRAINT contratado_cpf_key;
ALTER TABLE contratado DROP CONSTRAINT contratado_email_key;
CREATE UNIQUE INDEX idx_unique_contratado_cnpj_ativo ON contratado (cnpj) WHERE ativo IS TRUE;
CREATE UNIQUE INDEX idx_unique_contratado_cpf_ativo ON contratado (cpf) WHERE ativo IS TRUE;
CREATE UNIQUE INDEX idx_unique_contratado_email_ativo ON contratado (email) WHERE ativo IS TRUE;

-- Correção para a tabela: usuario (para campos que devem ser únicos quando ativos)
ALTER TABLE usuario DROP CONSTRAINT usuario_email_key;
ALTER TABLE usuario DROP CONSTRAINT usuario_cpf_key;
ALTER TABLE usuario DROP CONSTRAINT usuario_matricula_key;
CREATE UNIQUE INDEX idx_unique_usuario_email_ativo ON usuario (email) WHERE ativo IS TRUE;
CREATE UNIQUE INDEX idx_unique_usuario_cpf_ativo ON usuario (cpf) WHERE ativo IS TRUE;
CREATE UNIQUE INDEX idx_unique_usuario_matricula_key ON usuario (matricula) WHERE ativo IS TRUE;

-- Correção para a tabela: contrato
ALTER TABLE contrato DROP CONSTRAINT contrato_nr_contrato_key;
CREATE UNIQUE INDEX idx_unique_contrato_nr_contrato_ativo ON contrato (nr_contrato) WHERE ativo IS TRUE;



flask seed-db para popular o banco de dados com dados iniciais

INSERT INTO perfil (id, nome) VALUES (1, 'Administrador');
INSERT INTO perfil (id, nome) VALUES (2, 'Gestor');
INSERT INTO perfil (id, nome) VALUES (3, 'Fiscal');



INSERT INTO modalidade (nome) VALUES ('Pregão');
INSERT INTO modalidade (nome) VALUES ('Concorrência');
INSERT INTO modalidade (nome) VALUES ('Concurso');
INSERT INTO modalidade (nome) VALUES ('Leilão');
INSERT INTO modalidade (nome) VALUES ('Diálogo Competitivo');
INSERT INTO modalidade (nome) VALUES ('Dispensa de Licitação');
INSERT INTO modalidade (nome) VALUES ('Inexigibilidade de Licitação');
INSERT INTO modalidade (nome) VALUES ('Credenciamento');

-- --- Populando a tabela 'status' (Status de Contratos) ---
-- Representa o ciclo de vida de um contrato.
INSERT INTO status (nome) VALUES ('Vigente');
INSERT INTO status (nome) VALUES ('Encerrado');
INSERT INTO status (nome) VALUES ('Rescindido');
INSERT INTO status (nome) VALUES ('Suspenso');
INSERT INTO status (nome) VALUES ('Aguardando Publicação');


-- --- Populando a tabela 'statusrelatorio' (Status de Relatórios de Fiscalização) ---
-- Representa o fluxo de aprovação de um relatório enviado.
INSERT INTO statusrelatorio (nome) VALUES ('Pendente de Análise');
INSERT INTO statusrelatorio (nome) VALUES ('Aprovado');
INSERT INTO statusrelatorio (nome) VALUES ('Rejeitado com Pendência');


-- --- Populando a tabela 'statuspendencia' (Status de Pendências de Relatórios) ---
-- Representa o estado de uma solicitação de relatório feita pelo admin.
INSERT INTO statuspendencia (nome) VALUES ('Pendente');
INSERT INTO statuspendencia (nome) VALUES ('Concluída');
INSERT INTO statuspendencia (nome) VALUES ('Cancelada');



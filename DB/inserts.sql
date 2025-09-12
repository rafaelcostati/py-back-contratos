ALTER TABLE arquivo ALTER COLUMN tipo_arquivo TYPE TEXT;

ALTER TABLE usuario ADD COLUMN ativo BOOLEAN NOT NULL DEFAULT TRUE;
ALTER TABLE contrato ADD COLUMN ativo BOOLEAN NOT NULL DEFAULT TRUE;
ALTER TABLE contratado ADD COLUMN ativo BOOLEAN NOT NULL DEFAULT TRUE;
ALTER TABLE contrato ALTER COLUMN documento TYPE integer USING documento::integer;


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



DROP TABLE IF EXISTS usuario;

CREATE TABLE usuario (
    _id serial PRIMARY KEY,
    criado_em timestamptz NOT NULL,
    alterado_em timestamptz NOT NULL,
    nome text NOT NULL,
    email text NOT NULL UNIQUE,
    ativo boolean NOT NULL
);

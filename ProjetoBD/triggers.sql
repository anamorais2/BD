--Trigger para inserir um usuário nas suas respetivas tabelas
CREATE OR REPLACE FUNCTION insert_usuario_trigger_function()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.tipo = 'consumidor' THEN
        INSERT INTO consumidor (usuario_nome_utilizador) VALUES (NEW.nome_utilizador);
    ELSIF NEW.tipo = 'administrador' THEN
        INSERT INTO administrador (usuario_nome_utilizador) VALUES (NEW.nome_utilizador);
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS insert_usuario_trigger ON usuario;

CREATE TRIGGER insert_usuario_trigger
AFTER INSERT ON usuario
FOR EACH ROW
EXECUTE FUNCTION insert_usuario_trigger_function();


-- Trigger para inserir um artista que contenha música na tabeça artista_musica
CREATE OR REPLACE FUNCTION insert_into_artista_musica()
    RETURNS TRIGGER
    LANGUAGE plpgsql
AS $$
DECLARE
    list_artistas_array TEXT[];
    total_elements INTEGER;
    i INTEGER;
    artista_nome TEXT;
BEGIN
    -- Converte a coluna list_artistas em um array de texto
    list_artistas_array := string_to_array(NEW.list_artistas, ',');

    total_elements := cardinality(list_artistas_array);

    FOR i IN 1..total_elements
    LOOP
        artista_nome := list_artistas_array[i];

        INSERT INTO artista_musica (artista_usuario_nome_utilizador, musica_ismn)
        VALUES (artista_nome, NEW.ismn);
    END LOOP;

    RETURN NEW; 
END;
$$;


DROP TRIGGER IF EXISTS insert_into_artista_musica_trigger ON musica;

CREATE TRIGGER insert_into_artista_musica_trigger
    AFTER INSERT ON musica
    FOR EACH ROW
    EXECUTE FUNCTION insert_into_artista_musica();

--Trigger para a coluna top_10 na tabela consumidor

CREATE OR REPLACE FUNCTION play_song_trigger()
    RETURNS TRIGGER AS $$
DECLARE
    user_consumidor text;
    musicas_ouvidas text[];
BEGIN
    user_consumidor := NEW.consumidor_usuario_nome_utilizador;

    -- Obter as 10 músicas mais ouvidas
    SELECT array_agg(subquery.musica_ismn::text ORDER BY subquery.views DESC)
    INTO musicas_ouvidas
    FROM (
        SELECT hm.musica_ismn, hm.views
        FROM historico_musica hm
        WHERE hm.consumidor_usuario_nome_utilizador = user_consumidor
        ORDER BY hm.views DESC
        LIMIT 10
    ) subquery;

    -- Atualizar o array de músicas na tabela consumidor
    UPDATE consumidor
    SET top_musicas = musicas_ouvidas
    WHERE usuario_nome_utilizador = user_consumidor;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


DROP TRIGGER IF EXISTS play_song_trigger ON historico_musica;

CREATE TRIGGER play_song_trigger
AFTER INSERT OR UPDATE ON historico_musica
FOR EACH ROW
EXECUTE FUNCTION play_song_trigger();







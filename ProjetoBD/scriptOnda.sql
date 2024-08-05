CREATE TABLE consumidor (
	usuario_nome_utilizador VARCHAR(20),
	PRIMARY KEY(usuario_nome_utilizador)
);

CREATE TABLE assinatura_historico_compra (
	id_assinatura			 BIGINT,
	tipo_assinatura			 VARCHAR(10) NOT NULL,
	data_inicio_assi			 DATE NOT NULL,
	data_fim_assi			 DATE NOT NULL,
	cartoes_utilizados		 TEXT,
	historico_compra_datahora		 TIMESTAMP NOT NULL,
	cartao_pre_pago_id_cartao		 BIGINT NOT NULL,
	consumidor_usuario_nome_utilizador VARCHAR(20) NOT NULL,
	PRIMARY KEY(id_assinatura)
);

CREATE TABLE artista (
	nome_artistico			 VARCHAR(50) NOT NULL,
	administrador_usuario_nome_utilizador VARCHAR(20) NOT NULL,
	gravadora_id_gravadora		 BIGINT NOT NULL,
	usuario_nome_utilizador		 VARCHAR(20),
	PRIMARY KEY(usuario_nome_utilizador)
);

CREATE TABLE usuario (
	nome_utilizador VARCHAR(20),
	nome		 VARCHAR(50) NOT NULL,
	morada		 VARCHAR(50) NOT NULL,
	email		 VARCHAR(50) NOT NULL,
	contacto	 BIGINT NOT NULL,
	password	 VARCHAR(500) NOT NULL,
	tipo		 VARCHAR(50) NOT NULL,
	PRIMARY KEY(nome_utilizador)
);

CREATE TABLE administrador (
	usuario_nome_utilizador VARCHAR(20),
	PRIMARY KEY(usuario_nome_utilizador)
);

CREATE TABLE musica (
	ismn		 BIGSERIAL,
	genero	 VARCHAR(20) NOT NULL,
	titulo	 VARCHAR(20) NOT NULL,
	data_lanc	 DATE NOT NULL,
	duracao	 INTEGER NOT NULL,
	list_artistas	 TEXT NOT NULL,
	album_id_album BIGINT,
	PRIMARY KEY(ismn)
);

CREATE TABLE album (
	id_album	 BIGSERIAL,
	titulo	 VARCHAR(20) NOT NULL,
	data_lanc DATE NOT NULL,
	PRIMARY KEY(id_album)
);

CREATE TABLE gravadora (
	id_gravadora BIGSERIAL,
	nome	 VARCHAR(20) NOT NULL,
	PRIMARY KEY(id_gravadora)
);

CREATE TABLE cartao_pre_pago (
	id_cartao				 BIGSERIAL,
	data_limite				 DATE NOT NULL,
	preco				 FLOAT(8) NOT NULL,
	consumidor_usuario_nome_utilizador	 VARCHAR(20) NOT NULL,
	administrador_usuario_nome_utilizador VARCHAR(20) NOT NULL,
	PRIMARY KEY(id_cartao)
);

CREATE TABLE lista_reproducao (
	id_lista					 BIGSERIAL,
	nome					 VARCHAR(20) NOT NULL,
	publica					 BOOL NOT NULL,
	assinatura_historico_compra_id_assinatura BIGINT NOT NULL,
	PRIMARY KEY(id_lista)
);

CREATE TABLE comentario (
	id_comentario			 BIGSERIAL,
	data				 TIMESTAMP NOT NULL,
	texto				 TEXT NOT NULL,
	comentario_id_comentario		 BIGINT,
	consumidor_usuario_nome_utilizador VARCHAR(20) NOT NULL,
	musica_ismn			 BIGINT NOT NULL,
	PRIMARY KEY(id_comentario)
);

CREATE TABLE historico_musica (
	datahora				 TIMESTAMP NOT NULL,
	views				 INTEGER NOT NULL,
	musica_ismn			 BIGINT,
	consumidor_usuario_nome_utilizador VARCHAR(20),
	PRIMARY KEY(musica_ismn,consumidor_usuario_nome_utilizador)
);

CREATE TABLE consumidor_lista_reproducao (
	consumidor_usuario_nome_utilizador VARCHAR(20),
	lista_reproducao_id_lista		 BIGINT,
	PRIMARY KEY(consumidor_usuario_nome_utilizador,lista_reproducao_id_lista)
);

CREATE TABLE consumidor_album (
	consumidor_usuario_nome_utilizador VARCHAR(20),
	album_id_album			 BIGINT,
	PRIMARY KEY(consumidor_usuario_nome_utilizador,album_id_album)
);

CREATE TABLE lista_reproducao_musica (
	lista_reproducao_id_lista BIGINT,
	musica_ismn		 BIGINT,
	PRIMARY KEY(lista_reproducao_id_lista,musica_ismn)
);

CREATE TABLE artista_musica (
	artista_usuario_nome_utilizador VARCHAR(20),
	musica_ismn			 BIGINT,
	PRIMARY KEY(artista_usuario_nome_utilizador,musica_ismn)
);

ALTER TABLE consumidor ADD CONSTRAINT consumidor_fk1 FOREIGN KEY (usuario_nome_utilizador) REFERENCES usuario(nome_utilizador);
ALTER TABLE assinatura_historico_compra ADD CONSTRAINT assinatura_historico_compra_fk1 FOREIGN KEY (cartao_pre_pago_id_cartao) REFERENCES cartao_pre_pago(id_cartao);
ALTER TABLE assinatura_historico_compra ADD CONSTRAINT assinatura_historico_compra_fk2 FOREIGN KEY (consumidor_usuario_nome_utilizador) REFERENCES consumidor(usuario_nome_utilizador);
ALTER TABLE artista ADD CONSTRAINT artista_fk1 FOREIGN KEY (administrador_usuario_nome_utilizador) REFERENCES administrador(usuario_nome_utilizador);
ALTER TABLE artista ADD CONSTRAINT artista_fk2 FOREIGN KEY (gravadora_id_gravadora) REFERENCES gravadora(id_gravadora);
ALTER TABLE artista ADD CONSTRAINT artista_fk3 FOREIGN KEY (usuario_nome_utilizador) REFERENCES usuario(nome_utilizador);
ALTER TABLE usuario ADD UNIQUE (email, contacto);
ALTER TABLE administrador ADD CONSTRAINT administrador_fk1 FOREIGN KEY (usuario_nome_utilizador) REFERENCES usuario(nome_utilizador);
ALTER TABLE musica ADD CONSTRAINT musica_fk1 FOREIGN KEY (album_id_album) REFERENCES album(id_album);
ALTER TABLE cartao_pre_pago ADD CONSTRAINT cartao_pre_pago_fk1 FOREIGN KEY (consumidor_usuario_nome_utilizador) REFERENCES consumidor(usuario_nome_utilizador);
ALTER TABLE cartao_pre_pago ADD CONSTRAINT cartao_pre_pago_fk2 FOREIGN KEY (administrador_usuario_nome_utilizador) REFERENCES administrador(usuario_nome_utilizador);
ALTER TABLE lista_reproducao ADD CONSTRAINT lista_reproducao_fk1 FOREIGN KEY (assinatura_historico_compra_id_assinatura) REFERENCES assinatura_historico_compra(id_assinatura);
ALTER TABLE comentario ADD CONSTRAINT comentario_fk1 FOREIGN KEY (comentario_id_comentario) REFERENCES comentario(id_comentario);
ALTER TABLE comentario ADD CONSTRAINT comentario_fk2 FOREIGN KEY (consumidor_usuario_nome_utilizador) REFERENCES consumidor(usuario_nome_utilizador);
ALTER TABLE comentario ADD CONSTRAINT comentario_fk3 FOREIGN KEY (musica_ismn) REFERENCES musica(ismn);
ALTER TABLE historico_musica ADD CONSTRAINT historico_musica_fk1 FOREIGN KEY (musica_ismn) REFERENCES musica(ismn);
ALTER TABLE historico_musica ADD CONSTRAINT historico_musica_fk2 FOREIGN KEY (consumidor_usuario_nome_utilizador) REFERENCES consumidor(usuario_nome_utilizador);
ALTER TABLE consumidor_lista_reproducao ADD CONSTRAINT consumidor_lista_reproducao_fk1 FOREIGN KEY (consumidor_usuario_nome_utilizador) REFERENCES consumidor(usuario_nome_utilizador);
ALTER TABLE consumidor_lista_reproducao ADD CONSTRAINT consumidor_lista_reproducao_fk2 FOREIGN KEY (lista_reproducao_id_lista) REFERENCES lista_reproducao(id_lista);
ALTER TABLE consumidor_album ADD CONSTRAINT consumidor_album_fk1 FOREIGN KEY (consumidor_usuario_nome_utilizador) REFERENCES consumidor(usuario_nome_utilizador);
ALTER TABLE consumidor_album ADD CONSTRAINT consumidor_album_fk2 FOREIGN KEY (album_id_album) REFERENCES album(id_album);
ALTER TABLE lista_reproducao_musica ADD CONSTRAINT lista_reproducao_musica_fk1 FOREIGN KEY (lista_reproducao_id_lista) REFERENCES lista_reproducao(id_lista);
ALTER TABLE lista_reproducao_musica ADD CONSTRAINT lista_reproducao_musica_fk2 FOREIGN KEY (musica_ismn) REFERENCES musica(ismn);
ALTER TABLE artista_musica ADD CONSTRAINT artista_musica_fk1 FOREIGN KEY (artista_usuario_nome_utilizador) REFERENCES artista(usuario_nome_utilizador);
ALTER TABLE artista_musica ADD CONSTRAINT artista_musica_fk2 FOREIGN KEY (musica_ismn) REFERENCES musica(ismn);

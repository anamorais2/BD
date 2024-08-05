##
## =============================================
## ============== Bases de Dados ===============
## ============== LEI  2022/2023 ===============
## =============================================
## =============================================
## =============================================
## === Department of Informatics Engineering ===
## =========== University of Coimbra ===========
## =============================================
##
## Authors:
##   Ana Carolina dos Santos Morais <anamorais@student.dei.uc.pt>
##   Fernanda Margarida Rodrigues Fernandes <mfernandes@student.dei.uc.pt>
##   João Gonçalo Reis Lopes <uc2012170913@student.uc.pt>
##   
##   University of Coimbra


import flask
import logging
import psycopg2
import datetime
import calendar
import time
import jwt
import random

import hashlib 
from flask import jsonify, request



secret_key = 'superKey'

app = flask.Flask(__name__)


StatusCodes = {
    'success': 200,
    'api_error': 400,
    'internal_error': 500
}

##########################################################
## DATABASE ACCESS
##########################################################

def db_connection():
    db = psycopg2.connect(
        user= 'aulaspl',
        password='aulaspl',
        host='127.0.0.1',
        port='5432',
        database='dbproj'
    )

    return db


@app.route('/')
def landing_page():
    return """

    Hello World (Python Native)!  <br/>
    <br/>
    Check the sources for instructions on how to use the endpoints!<br/>
    <br/>
    BD 2022 Team<br/>
    <br/>
    """
##########################################################
## Verificações de dados
##########################################################
def check_contacto(numero):
    try:
        numero = str(numero)  
        numero = numero.replace(" ", "")
        return len(numero) == 9 and numero.isdigit() and numero[0] != '0'
    except:
        return False
    
def check_data(data):
    try:
        datetime.datetime.strptime(data, '%Y-%m-%d')
        ano, mes, dia = map(int, data.split('-'))
        datetime.datetime(ano, mes, dia)
        return True
    except (ValueError, TypeError):
        return False
    
def check_tipo(palavra):
    try:
        palavra = palavra.lower()
        return palavra == "consumidor" or palavra == "administrador"
    except:
        return False


##########################################################
## ENDPOINTS
##########################################################



@app.route("/login", methods=["PUT"])
def login():
    try:
        args = request.get_json()
    except:
        return jsonify({
            "status": StatusCodes['internal_error'],
            "error": "No JSON"
        })

    if "nome_utilizador" not in args or "password" not in args:
        return jsonify({
            "code": StatusCodes['api_error'],
            "message": "Wrong parameters"
        })

    nome_utilizador = args["nome_utilizador"]
    password = hashlib.sha256(args["password"].encode()).hexdigest()

    query = "SELECT password FROM usuario WHERE nome_utilizador = %s"
    message = {}

    try:
        with db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (nome_utilizador,))

                if cursor.rowcount == 0:
                    message["status"] = StatusCodes['api_error']
                    message["error"] = f"No user with that credentials: {nome_utilizador}"
                else:
                    row = cursor.fetchone()
                    if password == row[0]:
                        # Geração do token JWT
                        payload = {'nome_utilizador': nome_utilizador}
                        token = jwt.encode(payload, secret_key, algorithm='HS256')
                        message["status"] = StatusCodes['success']
                        message["token"] = token
                    else:
                        message["status"] = StatusCodes['api_error']
                        message["error"] = "Wrong Password"
                        
    except (Exception, psycopg2.DatabaseError) as error:
        
        return jsonify({
            "status": StatusCodes['internal_error'],
            "error": str(error)
        })
    

    finally:
        if conn is not None:
            conn.close()


    return jsonify(message)



@app.route("/register", methods=["POST"])
def register():
    # get and check args
    try:
        args = request.get_json()
    except:
        return jsonify({
            "status": StatusCodes['api_error'],
            "error": "No json"
        })

    message = {}
    
    #Registo de Artista
    if "nome_utilizador" in args and "nome" in args and "morada" in args and "email" in args and "contacto" in args and "password" in args and "nome_artistico" in args and "nome_gravadora" in args and "token" in args:
        username = args["nome_utilizador"]
        nome = args["nome"]
        morada = args["morada"]
        contacto = args["contacto"]  
        email = args["email"]
        password = hashlib.sha256(args["password"].encode()).hexdigest()
        nome_artistico = args["nome_artistico"]
        nome_gravadora = args["nome_gravadora"]
        tipo = "artista"   
        decoded_token = jwt.decode(args["token"], secret_key, algorithms=['HS256'])
        user_admin = decoded_token['nome_utilizador']  
        
        query_admin = f"SELECT * FROM administrador WHERE usuario_nome_utilizador like '{user_admin}'"
        query = "SELECT * FROM usuario WHERE nome_utilizador like %s"
        values = (username,)
        query_grav = "SELECT * FROM gravadora WHERE nome like %s"
        values_grav = (nome_gravadora,)
        
        
        
        try:
            with db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query_admin)
                    if cursor.rowcount == 1:
                        cursor.execute(query, values)
                        if cursor.rowcount == 0:
                            cursor.execute(query_grav,values_grav)
                            if cursor.rowcount == 0:
                                query = f"INSERT INTO gravadora (nome) VALUES ('{nome_gravadora}')"
                                cursor.execute(query)
                                
                            if check_contacto(contacto):    
                                query = "INSERT INTO usuario (nome_utilizador, nome, morada, email, contacto, password, tipo) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                                values = (username, nome, morada, email, contacto, password,tipo,)
                                cursor.execute(query, values)
        
                                query = "INSERT INTO artista (nome_artistico, administrador_usuario_nome_utilizador, gravadora_id_gravadora, usuario_nome_utilizador) VALUES (%s,%s,(SELECT id_gravadora FROM gravadora WHERE nome like %s),%s)"
                                values = (nome_artistico,user_admin,nome_gravadora,username)
                                cursor.execute(query, values)
                                
                                conn.commit()
        
                                message["status"] = StatusCodes['success']
                                message["message"] = "Registration completed"
                                message["result"] = f"{username}"
                                
                            else:
                                message["status"] = StatusCodes['api_error']
                                message["error"] = "Incorrect phone number"
                                
                        else:
                            message["status"] = StatusCodes['api_error']
                            message["error"] = "Username already registered"
                    else:
                        message["status"] = StatusCodes['api_error']
                        message["error"] = "Only administrators can register artists"
                        
        except (Exception, psycopg2.DatabaseError) as error:
            return jsonify({
                "status": StatusCodes['internal_error'],
                "error": str(error)
            })
        
            # an error occurred, rollback
            conn.rollback()

        finally:
            if conn is not None:
                conn.close()
                
           #Administradores e Consumidores (É necessário registar os administradores por causa do hash)
    elif "nome_utilizador" in args and "nome" in args and "morada" in args and "contacto" in args and "email" in args and "password" in args and "tipo" in args:
        username = args["nome_utilizador"]
        nome = args["nome"]
        morada = args["morada"]
        contacto = args["contacto"]  
        email = args["email"]
        password = hashlib.sha256(args["password"].encode()).hexdigest()
        tipo = args["tipo"]

        # Check if person already registered
        query = "SELECT * FROM usuario WHERE nome_utilizador like %s"
        values = (username,)

        try:
            with db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, values)

                    if cursor.rowcount == 0:
                        
                        if check_contacto(contacto) and check_tipo(tipo):
                            query = "INSERT INTO usuario (nome_utilizador, nome, morada, email, contacto, password, tipo) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                            values = (username, nome, morada, email, contacto, password,tipo,)
                            cursor.execute(query, values)
                            
                            conn.commit()
    
                            message["status"] = StatusCodes['success']
                            message["message"] = "Registration completed"
                            message["result"] = f"{username}"
                            
                        else:
                            message["status"] = StatusCodes['api_error']
                            message["error"] = "Incorrect phone number or incorrect type"
                    else:
                        message["status"] = StatusCodes['api_error']
                        message["error"] = "Username already registered"

        except (Exception, psycopg2.DatabaseError) as error:
            return jsonify({
                "status": StatusCodes['internal_error'],
                "error": str(error)
            })
        
            # an error occurred, rollback
            conn.rollback()

        finally:
            if conn is not None:
                conn.close()

    else:
        return jsonify({
            "status": StatusCodes['api_error'],
            "error": "Wrong parameters"
        })


    return jsonify(message)



@app.route('/artist_info/<user_artista>', methods=['GET'])
def get_infoArtista(user_artista): #Assumimos que o nome artistico não é único, por isso optámos por colocar o nome_utilizador
    
    logger.info('GET /artist_info/<nome_artista>')

    logger.debug(f'nome_artistico: {user_artista}')
    
    message = {}
    query = """SELECT
        a.nome_artistico AS Nome_Artista,
        m.ismn AS ISMN,
        m.titulo AS Titulo_Musica,
        m.album_id_album AS ID_Album,
        al.titulo AS Titulo_Album,
        g.nome AS Nome_Gravadora,
        lr.id_lista AS ID_Lista_Reproducao
    FROM
        artista AS a
        LEFT JOIN artista_musica AS am ON a.usuario_nome_utilizador = am.artista_usuario_nome_utilizador
        LEFT JOIN musica AS m ON am.musica_ismn = m.ismn
        LEFT JOIN album AS al ON m.album_id_album = al.id_album
        LEFT JOIN gravadora AS g ON a.gravadora_id_gravadora = g.id_gravadora
        LEFT JOIN lista_reproducao_musica AS lrm ON m.ismn = lrm.musica_ismn
        LEFT JOIN lista_reproducao AS lr ON lrm.lista_reproducao_id_lista = lr.id_lista
    WHERE
        a.usuario_nome_utilizador = %s
        AND (lr.publica IS NULL OR lr.publica = true)
    """
    
    try:
        with db_connection() as conn:
            with conn.cursor() as cursor: 
               cursor.execute(query, (user_artista,))
               rows = cursor.fetchall()
               if rows != 0:

                   artist_name = None
                   record_label = None
                   songs = []
                   albums = []
                   playlists = []
                   existing_music = set() 
                   existing_album = set() 

                   for row in rows:
                       if artist_name is None:
                           artist_name = row[0]
                           record_label = row[5]
                      
                       song_id = row[1]
                       song_title = row[2]
                       songs.append({'song_id':song_id,'song_title': song_title})
    
                       album_id = row[3]
                       album_title = row[4]
                       if album_title is not None and album_id not in existing_album:
                           existing_album.add(album_id)
                           albums.append({'album_id':album_id,'album_title': album_title})
    
                       playlist_id = row[6]
                       if playlist_id is not None and playlist_id not in existing_music:
                           existing_music.add(playlist_id)  # Adiciona o id ao conjunto de ids existentes
                           playlists.append({'playlist_id': playlist_id})

                   content = {
                             'artist_name': artist_name,
                              'record_label': record_label,
                              'songs': songs,
                              'albums': albums,
                              'playlists': playlists
                            }
               
                   message["status"] = StatusCodes['success']
                   message["results"] = content
    
        
    except (Exception, psycopg2.DatabaseError) as error:
        return jsonify({
            "status": StatusCodes['internal_error'],
            "error": str(error)
        })

    return jsonify(message)


@app.route('/song', methods=['POST'])
def add_song():
    # get and check args
    try:
        args = request.get_json()
    except:
        return jsonify({
            "status": StatusCodes['api_error'],
            "error": "No json"
        })

    if "genero" not in args or "titulo" not in args or "data_lanc" not in args or "duracao" not in args or "list_artistas" not in args or "token" not in args:
        return jsonify({
            "status": StatusCodes['api_error'],
            "error": "Wrong parameters"
        })
    
    genero = args["genero"]
    titulo = args["titulo"]
    data_lanc = args["data_lanc"]
    duracao = args["duracao"]
    list_artistas = args["list_artistas"]
    decoded_token = jwt.decode(args["token"], secret_key, algorithms=['HS256'])
    user_artista = decoded_token['nome_utilizador']
    
    list_artistas.append( user_artista)
    
    lista =  ",".join(list_artistas) 
    
    message = {}
    query = "SELECT * FROM artista WHERE usuario_nome_utilizador = %s;"
    query_insert = f"INSERT INTO musica (ismn, genero, titulo, data_lanc, duracao, album_id_album,list_artistas) VALUES ((SELECT COALESCE(MAX(ismn), 0) + 1 FROM musica), '{genero}', '{titulo}', '{data_lanc}', {duracao}, null,'{lista}') RETURNING ismn;"
    try:
        with db_connection() as conn:
            with conn.cursor() as cursor: 
                cursor.execute(query, (user_artista,))
                if cursor.rowcount == 1:
                    if check_data(data_lanc):
                        cursor.execute(query_insert)
                        row = cursor.fetchone()
                        ismn = row[0]
                        
                        conn.commit()
    
                        message["status"] = StatusCodes['success']
                        message["message"] = "Song added successfully"
                        message["results"] = ismn
                    else:
                        message["status"] = StatusCodes['api_error']
                        message["error"] = "Wrong date"
                        
                else:
                    message["status"] = StatusCodes['api_error']
                    message["error"] = "Only artists can manage songs"
                    
    except (Exception, psycopg2.DatabaseError) as error:
        return jsonify({
            "status": StatusCodes['internal_error'],
            "error": str(error)
        })
    
        # an error occurred, rollback
        conn.rollback()

    finally:
        if conn is not None:
            conn.close()

    return jsonify(message)



@app.route('/album', methods=['POST'])
def add_album():
    # get and check args
    try:
        args = request.get_json()
    except:
        return jsonify({
            "status": StatusCodes['api_error'],
            "error": "No json"
        })

    if "titulo" not in args or "data_lanc" not in args or "list_songs" not in args or "token" not in args:
        return jsonify({
            "status": StatusCodes['api_error'],
            "error": "Wrong parameters"
        })

    titulo = args["titulo"]
    data_lanc = args["data_lanc"]
    songs = args["list_songs"]
    decoded_token = jwt.decode(args["token"], secret_key, algorithms=['HS256'])
    user_artista = decoded_token['nome_utilizador']

    message = {}
    query = "SELECT * FROM artista WHERE usuario_nome_utilizador = %s;"
    query_insert = "INSERT INTO album (id_album, titulo, data_lanc) VALUES ((SELECT COALESCE(MAX(id_album), 0) + 1 FROM album), %s,%s) RETURNING id_album"

    try:
        with db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (user_artista,))
                if cursor.rowcount == 1:
                    if check_data(data_lanc):
                        cursor.execute(query_insert, (titulo, data_lanc,))
                        album_id = cursor.fetchone()[0]
    
                        for song in songs:
                            if isinstance(song, dict):  # Verifica se é um dicionário
                                genero = song["genero"]
                                titulo = song["titulo"]
                                data_lanc = song["data_lanc"]
                                duracao = song["duracao"]
                                lista_artistas = song["lista_artistas"]
    
                                lista_artistas.append(user_artista)
                                lista = ",".join(lista_artistas)
                                
                                if check_data(data_lanc):   
                                    query_insert = f"INSERT INTO musica (ismn, genero, titulo, data_lanc, duracao, album_id_album,list_artistas) VALUES ((SELECT COALESCE(MAX(ismn), 0) + 1 FROM musica), '{genero}', '{titulo}', '{data_lanc}', {duracao}, {album_id},'{lista}') RETURNING ismn;"
                                    cursor.execute(query_insert)
                                    row = cursor.fetchone()
                                    ismn = row[0]
        
                                    # Verificar se existem artistas na aplicação associados a uma música
                                    for artista in lista_artistas:
                                        query = "SELECT * FROM artista_musica WHERE artista_usuario_nome_utilizador = %s AND musica_ismn = %s;"
                                        cursor.execute(query, (artista,ismn,))
                                        if cursor.rowcount == 0:
                                            query_insert_insert = "INSERT INTO artista_musica (artista_usuario_nome_utilizador, musica_ismn) VALUES (%s, %s);"
                                            cursor.execute(query_insert_insert, (artista, ismn,))
                                else:
                                    message["status"] = StatusCodes['api_error']
                                    message["error"] = "Wrong date"
                                    return jsonify(message)
                                    
                            elif isinstance(song, int):  # Verifica se é um número inteiro
                                query = "SELECT * FROM artista_musica WHERE musica_ismn = %s AND artista_usuario_nome_utilizador LIKE %s;"  # Verificar se a música pertence ao artista
                                cursor.execute(query, (song, user_artista,))
                                if cursor.rowcount == 1:
                                    query_update = "UPDATE musica SET album_id_album = %s WHERE ismn = %s;"
                                    cursor.execute(query_update, (album_id, song,))
                                else:
                                    message["status"] = StatusCodes['api_error']
                                    message["error"] = f"Song {song} not found"
                                    conn.rollback()
                                    return jsonify(message)
    
                            else:
                                message["status"] = StatusCodes['api_error']
                                message["error"] = "Invalid song format"
                                conn.rollback()
                                return jsonify(message)
    
                        conn.commit()
    
                        message["status"] = StatusCodes['success']
                        message["message"] = "Album added successfully"
                        message["results"] = album_id
                    else:
                        message["status"] = StatusCodes['api_error']
                        message["error"] = "Wrong date"
                        
                else:
                    message["status"] = StatusCodes['api_error']
                    message["error"] = "Only artists can manage albums"

    except (Exception, psycopg2.DatabaseError) as error:
        return jsonify({
            "status": StatusCodes['internal_error'],
            "error": str(error)
        })

        # an error occurred, rollback
        conn.rollback()

    finally:
        if conn is not None:
            conn.close()

    return jsonify(message)




@app.route('/subcription', methods=['POST'])
def subscribe_premium():
    logger.info('POST /subcription')
    
    # get and check args
    
    try:
        args = request.get_json()
        
    except:
        return jsonify({
            "status": StatusCodes['api_error'],
            "error": "No json"
        })

    
    if "tipo_assinatura" not in args or "lista_cartoes" not in args or "token" not in args:
        
        return jsonify({
            "status": StatusCodes['api_error'],
            "error": "Wrong parameters"
        })

    tipo_assinatura = args["tipo_assinatura"]
    lista_cartoes = args["lista_cartoes"]
    decoded_token = jwt.decode(args["token"], secret_key, algorithms=['HS256'])
    user_consumidor = decoded_token['nome_utilizador']
    
    data_atual = datetime.date.today()
        

    query = f"Select * from consumidor where usuario_nome_utilizador like '{user_consumidor}' FOR UPDATE" #Verificar se o consumidor existe e Lock para a consistência de dados
    query_consu = f"SELECT * FROM assinatura_historico_compra WHERE consumidor_usuario_nome_utilizador LIKE '{user_consumidor}' AND '{data_atual}' BETWEEN data_inicio_assi AND data_fim_assi ORDER BY historico_compra_datahora DESC LIMIT 1;" #Verificar se contem outra assinatura

    
    lista_cartoes_uteis = []
    card_user = []
    
    message = {}

    try:
        with db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)
                if cursor.rowcount == 1:
                    
                    if(tipo_assinatura == "month" ):
                        price = 7
                        data_limite = data_atual + datetime.timedelta(days=30)
                    elif(tipo_assinatura == "quarter"):
                        price = 21
                    elif(tipo_assinatura == "semester"):
                        price = 42
                    else:
                        message["status"] = StatusCodes['api_error']
                        message["error"]  = "Wrong subscription type, choose one of the following options: 'month' | 'quarter' | 'semester'"
                        return jsonify(message)
                    
                    for card in lista_cartoes:
                        query = f"SELECT * FROM cartao_pre_pago where id_cartao = {card} and consumidor_usuario_nome_utilizador like '{user_consumidor}' and preco > 0 and data_limite > '{data_atual}';" #Verificar se o cartão pode ser usado
                        cursor.execute(query)
                        row = cursor.fetchone()
                        if cursor.rowcount == 1:
                            lista_cartoes_uteis.append([card,row[1]])
                            
                    if len(lista_cartoes_uteis) == 0:
                        message["status"] = StatusCodes['api_error']
                        message["error"]  = "no associated card"
                        return jsonify(message)
                    

                    cursor.execute(query_consu)
                    
                    if cursor.rowcount == 0: #Ou seja primeira assinatura
                        if(tipo_assinatura == "month" ):
                            data_limite = data_atual + datetime.timedelta(days=30)
                        elif(tipo_assinatura == "quarter"):
                            data_limite = data_atual + datetime.timedelta(days=90)
                        elif(tipo_assinatura == "semester"):
                            data_limite = data_atual + datetime.timedelta(days=120)     
                    else:
                        row = cursor.fetchone()
                        data_atual = row[3]
                        if(tipo_assinatura == "month" ):
                            price = 7
                            data_limite = data_atual + datetime.timedelta(days=30)
                        elif(tipo_assinatura == "quarter"):
                            price = 21
                            data_limite = data_atual + datetime.timedelta(days=90)
                        elif(tipo_assinatura == "semester"):
                            price = 42
                            data_limite = data_atual + datetime.timedelta(days=120)
                            
                    saldo_disponivel = sum(row[1] for row in lista_cartoes_uteis)

                    if saldo_disponivel < price:
                        message["status"] = StatusCodes['api_error']
                        message["error"]  = "Insufficient balance to cover the amount"
                        return jsonify(message)
                        
                   
                    for indice, row in enumerate(lista_cartoes_uteis):
                        saldo_atual = row[1]
                        
                        if saldo_atual >= price:
                            #O saldo atual do cartão é suficiente para cobrir o valor."
                            valor_pago = price
                            saldo_atual -= price
                            card_user.append((row[0], valor_pago))
                            break
                        
                        if saldo_atual > 0:
                            # O saldo atual do cartão está parcialmente utilizado
                            valor_pago = saldo_atual
                            price -= saldo_atual
                            saldo_atual = 0
                            card_user.append((row[0], valor_pago))
                        
                        if indice + 1 < len(lista_cartoes_uteis) and price > 0:
                            # Há mais cartões disponíveis e ainda há valor a ser pago
                            proximo_saldo = lista_cartoes_uteis[indice + 1][1]
                            if proximo_saldo >= price:
                                # O saldo do próximo cartão é suficiente para cobrir o valor restante
                                valor_pago = price
                                proximo_saldo -= price
                                card_user.append((lista_cartoes_uteis[indice + 1][0], valor_pago))
                                break
                            
                            if proximo_saldo > 0:
                                # O saldo do próximo cartão está parcialmente utilizado
                                valor_pago = proximo_saldo
                                price -= proximo_saldo
                                proximo_saldo = 0
                                card_user.append((lista_cartoes_uteis[indice + 1][0], valor_pago))
                                lista_cartoes_uteis[indice + 1][1] = proximo_saldo
                            
                    for cartao_id, valor_pago in card_user:
                        update_query = "UPDATE cartao_pre_pago SET preco = preco - %s WHERE id_cartao = %s"
                        cursor.execute(update_query, (valor_pago, cartao_id))

                    data = time.strftime("%Y-%m-%d %H:%M:%S")
                
                    cartoes_utilizados_ids = [cartao_id for cartao_id, _ in card_user]
                    cartoes_utilizados_str = ','.join(map(str, cartoes_utilizados_ids[1:]))
                    query_assinatura = f"""INSERT INTO assinatura_historico_compra (id_assinatura,tipo_assinatura,data_inicio_assi,data_fim_assi,historico_compra_datahora,cartao_pre_pago_id_cartao,consumidor_usuario_nome_utilizador,
        cartoes_utilizados) VALUES ((SELECT COALESCE(MAX(id_assinatura), 0) + 1 FROM assinatura_historico_compra),'{tipo_assinatura}','{data_atual}','{data_limite}','{data}',{cartoes_utilizados_ids[0]},'{user_consumidor}','{cartoes_utilizados_str}')RETURNING id_assinatura;"""
                    cursor.execute(query_assinatura)
                    row = cursor.fetchone()
                    
                    conn.commit()
                    
                    message["status"]  = StatusCodes['success']
                    message["message"] = "SUBSCRIPTION COMPLETED"
                    message["result"] = row[0]
                                                           
                else:
                    message["status"] = StatusCodes['api_error']
                    message["error"]  = "only consumers can purchase a subscription"


    except (Exception, psycopg2.DatabaseError) as error:
        
        return jsonify({
            "status": StatusCodes['internal_error'],
            "error": str(error)
        })
    
        # an error occurred, rollback
        conn.rollback()

    finally:
        if conn is not None:
            conn.close()


    return jsonify(message)


@app.route('/card', methods=['POST'])
def generate_card():
    logger.info('POST /card')
    # get and check args
    try:
        args = request.get_json()
    except:
        return jsonify({
            "status": StatusCodes['api_error'],
            "error": "No json"
        })

    if "number_of_cards" not in args or "preco" not in args or "consumidor_nome_utilizador" not in args or "data_limite" not in args or "token" not in args:
        return jsonify({
            "status": StatusCodes['api_error'],
            "error": "Wrong parameters"
        })

    number_of_cards = args["number_of_cards"]
    preco = args["preco"]
    consumidor_nome_utilizador = args["consumidor_nome_utilizador"]
    data_limite = args["data_limite"]
    decoded_token = jwt.decode(args["token"], secret_key, algorithms=['HS256'])
    user_admin = decoded_token['nome_utilizador']

    message = {}
    query = f"""SELECT 'consumidor' AS tipo FROM consumidor WHERE usuario_nome_utilizador = '{consumidor_nome_utilizador}' UNION SELECT 'administrador' AS tipo FROM administrador WHERE usuario_nome_utilizador = '{user_admin}';"""
    lista_id_card = []

    try:
        with db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchall()
                if len(result) == 2:
                    if check_data(data_limite):
                        for i in range(number_of_cards):
                                
                            while True:
                                    
                                card_id = random.randint(10**15, (10**16)-1)
                                
                                # Verificar se o número já existe na tabela
                                query_check = f"SELECT COUNT(*) FROM cartao_pre_pago WHERE id_cartao = {card_id};"
                                cursor.execute(query_check)
                                count = cursor.fetchone()[0]
                                
                                if count == 0:
                                    # O número não existe na tabela, podemos prosseguir com a inserção
                                    break
                                
                            query = f"INSERT INTO cartao_pre_pago (id_cartao, preco, consumidor_usuario_nome_utilizador, administrador_usuario_nome_utilizador, data_limite) VALUES ({card_id}, {preco}, '{consumidor_nome_utilizador}', '{user_admin}', '{data_limite}');"
                            cursor.execute(query)
                                
                            lista_id_card.append(card_id)
                                
                        conn.commit()
        
                        message["status"] = StatusCodes['success']
                        message["message"] = f"{number_of_cards} cartões pré-pagos adicionados com sucesso"
                        message["results"] = lista_id_card
                        
                    else:
                        message["status"] = StatusCodes['api_error']
                        message["error"] = "Wrong Date"
                else:
                    message["status"] = StatusCodes['api_error']
                    message["error"] = "Only administrators can generate cards or Consumer not found"

    except (Exception, psycopg2.DatabaseError) as error:
        return jsonify({
            "status": StatusCodes['internal_error'],
            "error": str(error)
        })
    
        # an error occurred, rollback
        conn.rollback()

    finally:
        if conn is not None:
            conn.close()

    return jsonify(message)

@app.route('/playlist', methods=['POST'])
def create_playlist():
    # get and check args
    try:
        args = request.get_json()
    except:
        return jsonify({
            "status": StatusCodes['api_error'],
            "error": "No json"
        })

    if "playlist_name" not in args or "visibility" not in args or "songs" not in args or "token" not in args:
        return jsonify({
            "status": StatusCodes['api_error'],
            "error": "Wrong parameters"
        })
    
    playlist_name = args["playlist_name"]
    visibility = args["visibility"]
    songs = args["songs"]
    decoded_token = jwt.decode(args["token"], secret_key, algorithms=['HS256'])
    user_consumidor = decoded_token['nome_utilizador']

    data_atual = datetime.date.today()
    message = {}
    
    query = "SELECT * FROM consumidor WHERE usuario_nome_utilizador = %s;"

    query_assinatura =f"SELECT id_assinatura FROM assinatura_historico_compra WHERE consumidor_usuario_nome_utilizador LIKE '{user_consumidor}' AND '{data_atual}' BETWEEN data_inicio_assi AND data_fim_assi"

    
    try:
        with db_connection() as conn:
            with conn.cursor() as cursor: 
                cursor.execute(query, (user_consumidor,))
                if cursor.rowcount == 1:
                    cursor.execute(query_assinatura)
                    id_assinatura = cursor.fetchone()
                    if id_assinatura is not None: #Ou seja é assinante
                        id_assinatura = id_assinatura[0]
                        #Vamos validar se as músicas existem
                        for song in songs:
                            query = f"SELECT * FROM musica where ismn = {song} " 
                            cursor.execute(query)
                            if cursor.rowcount == 0:
                                message["status"] = StatusCodes['api_error']
                                message["error"] = f"Song: {song} not exist"
                                return jsonify(message)    
                            
                        query_insert = f"INSERT INTO lista_reproducao (id_lista, nome, publica, assinatura_historico_compra_id_assinatura) VALUES ((SELECT COALESCE(MAX(id_lista), 0) + 1 FROM lista_reproducao), '{playlist_name}', '{visibility}', {id_assinatura}) RETURNING id_lista"
                        cursor.execute(query_insert) 
                        id_lista = cursor.fetchone()[0] 
                        
                        query_insert_consumidor = f"INSERT INTO consumidor_lista_reproducao (consumidor_usuario_nome_utilizador,lista_reproducao_id_lista) VALUES ('{user_consumidor}',{id_lista})"
                        
                        cursor.execute(query_insert_consumidor)
                        
                        
                        for musica in songs:
                            query_insert_insert = f"INSERT INTO lista_reproducao_musica (lista_reproducao_id_lista, musica_ismn) VALUES((SELECT MAX(id_lista) FROM lista_reproducao),{musica})"
                            cursor.execute(query_insert_insert)
                    
                        
                        conn.commit()
                        
                        message["status"] = StatusCodes['success']
                        message["message"] = "Playlist created successfully"
                        message["results"] = id_lista
                        
                        
                    else:
                        message["status"] = StatusCodes['api_error']
                        message["error"] = f"The '{user_consumidor}' is not a subscriber"
                        return jsonify(message)        
                        
                        
                else:
                    message["status"] = StatusCodes['api_error']
                    message["error"] = "Only consumidores can manage playlist"
                    
    except (Exception, psycopg2.DatabaseError) as error:
        return jsonify({
            "status": StatusCodes['internal_error'],
            "error": str(error)
        })
    
        # an error occurred, rollback
        conn.rollback()

    finally:
        if conn is not None:
            conn.close()

    return jsonify(message)


@app.route('/comments/<int:ISMN>', methods=['POST'])
def leave_comment(ISMN):
    # get and check args
    try:
        args = request.get_json()
    except:
        return jsonify({
            "status": StatusCodes['api_error'],
            "error": "No json"
        })

    if "comment" not in args or "token" not in args:
        return jsonify({
            "status": StatusCodes['api_error'],
            "error": "Wrong parameters"
        })

    comment = args["comment"]
    decoded_token = jwt.decode(args["token"], secret_key, algorithms=['HS256'])
    user_consumidor = decoded_token['nome_utilizador']

    message = {}
    query = "SELECT * FROM musica WHERE ismn = %s;"

    try:
        with db_connection() as conn:
            with conn.cursor() as cursor: 
                cursor.execute(query, (ISMN,))
                if cursor.rowcount == 1:
                    
                    data = time.strftime("%Y-%m-%d %H:%M:%S")
                    
                    query_insert = f"INSERT INTO comentario (data, texto, comentario_id_comentario, consumidor_usuario_nome_utilizador, musica_ismn) VALUES ('{data}','{comment}',null,'{user_consumidor}',{ISMN}) RETURNING id_comentario"
                    cursor.execute(query_insert)
                    row = cursor.fetchone()

                    conn.commit()
                    
                    message["status"] = StatusCodes['success']
                    message["message"] = "Comment added successfully"
                    message["results"] = row[0]
                else:
                    message["status"] = StatusCodes['api_error']
                    message["error"] = "Music not found"
                    
    except (Exception, psycopg2.DatabaseError) as error:
        return jsonify({
            "status": StatusCodes['internal_error'],
            "error": str(error)
        })
    
        # an error occurred, rollback
        conn.rollback()

    finally:
        if conn is not None:
            conn.close()

    return jsonify(message)

@app.route('/comments/<int:ISMN>/<int:parent_comment_id>', methods=['POST'])
def reply_comment(ISMN,parent_comment_id):
    # get and check args
    try:
        args = request.get_json()
    except:
        return jsonify({
            "status": StatusCodes['api_error'],
            "error": "No json"
        })

    if "comment" not in args or "token" not in args:
        return jsonify({
            "status": StatusCodes['api_error'],
            "error": "Wrong parameters"
        })

    comment = args["comment"]
    decoded_token = jwt.decode(args["token"], secret_key, algorithms=['HS256'])
    user_consumidor = decoded_token['nome_utilizador']

    message = {}
    query = f"SELECT * FROM comentario WHERE id_comentario = '{parent_comment_id}';"
   

    try:
        with db_connection() as conn:
            with conn.cursor() as cursor: 
                cursor.execute(query)
                row = cursor.fetchall()[0]
                if row != 0:
                    
                    data = time.strftime("%Y-%m-%d %H:%M:%S")
                    
                    query_insert = f"INSERT INTO comentario (data, texto, comentario_id_comentario, consumidor_usuario_nome_utilizador, musica_ismn) VALUES ('{data}','{comment}',{parent_comment_id},'{user_consumidor}',{ISMN}) RETURNING id_comentario"
                    cursor.execute(query_insert)
                    row = cursor.fetchone()

                    conn.commit()
                    
                    message["status"] = StatusCodes['success']
                    message["message"] = "Comment added successfully"
                    message["results"] = row[0]
                else:
                    message["status"] = StatusCodes['api_error']
                    message["error"] = "Comment not found"
                    
    except (Exception, psycopg2.DatabaseError) as error:
        return jsonify({
            "status": StatusCodes['internal_error'],
            "error": str(error)
        })
    
        # an error occurred, rollback
        conn.rollback()

    finally:
        if conn is not None:
            conn.close()

    return jsonify(message)


@app.route('/song/<keyword>', methods=['GET'])
def search_song(keyword):
    logger.info('GET dbproj/song/<keyword>')
    logger.debug(f'keyword: {keyword}')

    conn = db_connection()
    c = conn.cursor()
    
    query = f"""SELECT m.titulo AS title, array_agg(a.nome_artistico) AS artists, array_agg(l.id_album) AS albums
            FROM musica m
            LEFT JOIN artista_musica am ON m.ismn = am.musica_ismn
            LEFT JOIN artista a ON am.artista_usuario_nome_utilizador = a.usuario_nome_utilizador
            LEFT JOIN album l ON m.album_id_album = l.id_album
            WHERE m.titulo LIKE '%{keyword}%'
            GROUP BY m.ismn
            ORDER BY m.titulo"""

    try:
        c.execute(query)
        rows = c.fetchall()
        results = []
        
        for row in rows:
            music = {'title': row[0], 'artists': row[1], 'albums': row[2]}
            results.append(music)
            logger.debug(row)

        response = {'status': StatusCodes['success'], 'results': results}

    except (Exception, psycopg2.DatabaseError) as error:
        return jsonify({
            "status": StatusCodes['internal_error'],
            "error": str(error)
        })

    finally:
        if conn is not None:
            conn.close()

    return jsonify(response)



@app.route('/<int:ismn>', methods=['PUT'])  
def play_song_(ismn):
    # get and check args
    try:
        args = request.get_json()
    except:
        return jsonify({
            "status": StatusCodes['api_error'],
            "error": "No json"
        })

    if "token" not in args:
        return jsonify({
            "status": StatusCodes['api_error'],
            "error": "Wrong parameters"
        })

    decoded_token = jwt.decode(args["token"], secret_key, algorithms=['HS256'])
    user_consumidor = decoded_token['nome_utilizador']

    message = {}
    query = f"SELECT * FROM consumidor WHERE usuario_nome_utilizador like '{user_consumidor}';"
    query_song = f"SELECT ismn FROM musica where ismn = {ismn}"
    query_album = f"SELECT album_id_album FROM musica where ismn = {ismn}"
    
    try:
        with db_connection() as conn:
            with conn.cursor() as cursor: 
                cursor.execute(query)
                if cursor.rowcount == 1:
                    cursor.execute(query_song)
                    if cursor.rowcount == 1:
                        cursor.execute(query_album)
                        row = cursor.fetchone()
                        if row[0] is not None: #Significa que a música não tem um álbum associado 
                            query_insert_album = f"INSERT INTO consumidor_album(consumidor_usuario_nome_utilizador,album_id_album) SELECT '{user_consumidor}', {row[0]} WHERE NOT EXISTS (SELECT 1 FROM consumidor_album WHERE consumidor_usuario_nome_utilizador = '{user_consumidor}' AND album_id_album = {row[0]});"  # Verificar se o registo já existe antes de inserir
                            cursor.execute(query_insert_album)
                        
                        query = f"SELECT * FROM historico_musica WHERE musica_ismn = {ismn} ORDER BY datahora DESC LIMIT 1;"
                        cursor.execute(query)
                        row = cursor.fetchone()  # Obter o último registo do histórico
                        if row is None:
                            data = time.strftime("%Y-%m-%d %H:%M:%S")                        
                            query_insert = f"INSERT INTO historico_musica (datahora, views, musica_ismn, consumidor_usuario_nome_utilizador) VALUES ('{data}',1,{ismn},'{user_consumidor}');"
                            cursor.execute(query_insert)
                        else:
                            data = time.strftime("%Y-%m-%d %H:%M:%S")
                            views =  row[1] 
                            query_insert = f"INSERT INTO historico_musica (datahora, views, musica_ismn, consumidor_usuario_nome_utilizador) VALUES ('{data}', {views}, {ismn}, '{user_consumidor}') ON CONFLICT (musica_ismn, consumidor_usuario_nome_utilizador) DO UPDATE SET views = excluded.views + 1, datahora = excluded.datahora;"
                            cursor.execute(query_insert)
                            
                        
                        conn.commit()
                        
                        message["status"] = StatusCodes['success']
                        message["message"] = "Music played successfully"
                              
                        
                    else:
                        message["status"] = StatusCodes['api_error']
                        message["error"] = "Music not found"
                        
                else:
                    message["status"] = StatusCodes['api_error']
                    message["error"] = "Only consumers can play a song"
                    
    except (Exception, psycopg2.DatabaseError) as error:
        return jsonify({
            "status": StatusCodes['internal_error'],
            "error": str(error)
        })

        # an error occurred, rollback
        conn.rollback()

    finally:
        if conn is not None:
            conn.close()

    return jsonify(message)




@app.route('/report/<year_month>', methods=['GET'])
def generate_monthly_report(year_month):
    
    linha = year_month.split('-')
    year = int(linha[0])
    month = int(linha[1])
    message = {}
    try:
        with db_connection() as conn:
            with conn.cursor() as cursor:
                _, num_days = calendar.monthrange(year, month)
                start_date = datetime.datetime(year, month, 1) - datetime.timedelta(days=365)
                end_date = datetime.datetime(year, month, num_days)
                
                query = """SELECT
                    DATE_TRUNC('month', datahora::timestamp) AS month_start,
                    musica.genero,
                    SUM(views) AS num_views
                FROM historico_musica
                INNER JOIN musica ON historico_musica.musica_ismn = musica.ismn
                WHERE datahora::timestamp >= %s AND datahora::timestamp <= %s
                GROUP BY month_start, musica.genero;"""
                
                cursor.execute(query, (start_date, end_date))
                results = cursor.fetchall()

        response_data = []
        for row in results:
            line = str(row[0]).split('-')
            response_data.append({
                'month': line[1]+'-'+line[0],
                'genre': row[1],
                'playbacks': row[2]
            })

        message["status"] = StatusCodes['success']
        message["results"] = response_data

    except (Exception, psycopg2.DatabaseError) as error:
        return jsonify({
            "status": StatusCodes['internal_error'],
            "error": str(error)
        })
    
    return jsonify(message)


if __name__ == '__main__':

    # set up logging
    logging.basicConfig(filename='log_file.log')
    logger = logging.getLogger('logger')
    logger.setLevel(logging.DEBUG)
    logger.debug("here")
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter('%(asctime)s [%(levelname)s]:  %(message)s', '%H:%M:%S')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    host = '127.0.0.1'
    port = 8080
    app.run(host=host, debug=True, threaded=True, port=port)
    logger.info(f'API v1.0 online: http://{host}:{port}')

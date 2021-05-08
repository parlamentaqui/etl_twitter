from flask import Blueprint, jsonify
from models import *
from unidecode import unidecode
from datetime import datetime
import requests
import os
from operator import attrgetter
import json

api = Blueprint('api', __name__, url_prefix='/api')
BEARER_TOKEN_TWITTER = os.getenv('BEARER_TOKEN')

# Token que autoriza a busca por dados na API do Twitter pelo protocolo OAuth 2.0 (somente infos publicas no Twitter)
auth_header = {"Authorization": "Bearer {}".format(BEARER_TOKEN_TWITTER)}


@api.route('/tweets')
def tweets():
    sorted_list = []
    sorted_list = sorted(Tweet.objects, key=attrgetter('date'))

    all_tweet = []

    for item in sorted_list[0:4]:
        all_tweet.insert(0, item.to_json())
    
    return jsonify(all_tweet)
    
# Rota que faz uma requsição à API do Twitter e retorna os perfis que são verificados (100 por vez)
@api.route('/perfis_deputados_verificados_100')
def encontra_perfis_verificados_100():
    
    # Separação de 100 usernames para cada requisição (já que existem 573 deputados no DB)
    usernames = ["usernames=","usernames=","usernames=","usernames=","usernames=","usernames="]

    cont = 0
    aux = 0

    # Recolhe os nomes dos deputados para colocar no paramêtro da requisição
    for item in Deputy.objects:
        if (cont % 100 != 0 or cont == 0) and cont != 572:
            usernames[aux] = usernames[aux] + str(item.name).replace(" ", "")[0:13] + ","
            cont += 1
        elif cont % 100 == 0:
            # Coloca no foramto correto 100 nomes de deputados para colocar na url da requisição
            usernames[aux] = usernames[aux][:-1]
            usernames[aux] = unidecode(usernames[aux]).replace(".", "").replace("'","").replace("-","")
            
            #Incrementa para poder iniciar mais 100 nomes já adicionando os deputados nas posições x00, preparando os pareametros da próxima requisição
            aux += 1
            usernames[aux] = usernames[aux] + str(item.name).replace(" ", "")[0:13] + ","
            cont += 1
        
        #Caso do último deputado no DB (tirando os de teste)
        else:
            usernames[aux] = usernames[aux] + str(item.name).replace(" ", "")[0:13] + ","
            usernames[aux] = usernames[aux][:-1]
            usernames[aux] = unidecode(usernames[aux]).replace(".", "").replace("'","").replace("-","")
            break

    # Lista com todos os resultados de cada nome de deputado
    json_deputies_usernames = []

    # Adiciona o resultado (jsons) de cada requsição com seus devidos parâmetros na lista
    for usernames_100 in usernames:
        json_deputies_usernames.append(metodo_de_request(usernames_100))

    # Lista com os deputados que são verificados
    json_deputies_verified = []

    # Procura os perfis que são verificados
    for r_result in json_deputies_usernames:
        for username in r_result['data']:
            if username['verified'] is True:
                json_deputies_verified.append(username)


    # Retorma o JSON com os deputados que possuem perfis verificados no Twitter
    return jsonify(json_deputies_verified)

# Metodo que faz os requests pra API dos usernames do Twitter e retorna os resultados em JSON
def metodo_de_request(usernames):
    r = requests.get(f"https://api.twitter.com/2/users/by?{usernames}&user.fields=verified,url", headers=auth_header)
    return r.json()

# Rota que retorna um tweet especifico pelo seu id
@api.route('/tweets_por_ids')
def busca_historico_tweet_por_id():
    
    tweet_ids = "ids=1376612438313852930" #Para adicionar mais ids, basta colocar a virrgula e o id sem espaço entre eles
    params = get_params_2()

    r = requests.get(f"https://api.twitter.com/2/tweets?{tweet_ids}", headers=auth_header, params=params)
    
    return r.json()



# Atualiza o banco de dados do twitter, colocando o username em deputados que possuem uma conta verificada
@api.route('/update_twitter_accounts')
def update_twitter_accounts():
    for item in Deputy.objects:

        #verificar se o edputado já tem seu twitter vinculado, se tiver, só passa pro próximo
        if item.twitter_username or item.twitter_id:
            continue

        #criar as chaves para pesquisa
        deputy_name = item.name
        deputy_name = unidecode(deputy_name).replace(".", "").replace("'","").replace("-","").replace(" ", "")[0:13]

        deputy_full_name = item.full_name
        deputy_full_name = unidecode(deputy_full_name).replace(".", "").replace("'","").replace("-","").replace(" ", "")[0:13]

        usernames_to_found = deputy_name + "," + deputy_full_name
        r = requests.get(f"https://api.twitter.com/2/users/by?usernames={usernames_to_found}&user.fields=verified,url", headers=auth_header)

        #caso a resposta seja nula, ignorar esse deputado
        if not r:
            print("Essa request não tem uma response") 
            continue 

        deputy_twitter_json = r.json()

        # Criar uma String para conseguir verificar se ele possue a chave data
        json_in_string = str(deputy_twitter_json)
        
        # if deputy_twitter_json.optString("data"):
        if "data" in json_in_string:
            #encontramos um deputado com conta

            for all_usermaes_fouded in deputy_twitter_json["data"]:
                if all_usermaes_fouded["verified"]:
                    #conta verificada, adicionar no item
                    item.twitter_username = all_usermaes_fouded["username"]
                    item.twitter_id = all_usermaes_fouded["id"]
                    
                    if len(all_usermaes_fouded["url"]) > 5:
                        item.website = all_usermaes_fouded["url"]
                    
                    item.save()
                    break
    
    return "Done. Use url api/get_all_deputies for get all the deputies in db"


# Rota que popula a classe Tweet com até 10 tweets mais recentes por usuario indicado pelo seu id
@api.route('/update_tweets')
def update_tweets():

    params = get_params_2()

    for deputy in Deputy.objects:
        
        if deputy.twitter_id:
            r = requests.get(f"https://api.twitter.com/2/users/{deputy.twitter_id}/tweets", headers=auth_header, params=params)

            if not r:
                continue
            
            last_10_tweets_json = r.json()['data']

            for tweet_json in last_10_tweets_json:
                # need_create = True
                
                # for tweet_item in Tweet.objects:
                #     if int(tweet_item.tweet_id) == int(tweet_json['id']):
                #         need_create = False
                #         break

                # if not need_create:
                #     continue

                new_tweet = Tweet(
                    tweet_id = str(tweet_json['id']),
                    deputy_id = deputy.id,
                    name = deputy.name,
                    twitter_username = deputy.twitter_username,
                    date = datetime.strptime(str(tweet_json["created_at"][0:18]), '%Y-%m-%dT%H:%M:%S') if tweet_json["created_at"] is not None else None,
                    source = tweet_json['text']
                ).save()

                #criar a lógica de atualização da ultima atividade recente do deputado em questão
                deputy.last_activity_date = new_tweet.date
                deputy.save()

    return "Updated tweets sucessfully. Now use /get_tweets to see the tweets"

# Pega parâmetros de informações que serão trazidas dos tweets (versao dessa rota)
def get_params_2():
    return "tweet.fields=created_at,id,author_id,text"

# Rota que retorna a informação de todos os deputados salvos no DB
@api.route('/get_all_deputies')
def get_all_deputies():
    t = []
    for item in Deputy.objects:
        t.append(item.to_json())

    return jsonify(t)

# Rota que apaga todos os objetos Tweets salvos no BD
@api.route('/get_all_tweets')
def index():
    tweets = []
    for item in Tweet.objects:
        tweets.append(item.to_json())

    return jsonify(tweets)

# Rota que deldeta todos os objetos Tweets salvos no BD
@api.route('/delete_all_tweets')
def delete_all_tweets():    
    Tweet.objects.all().delete()
    return "All tweets were deleted"


@api.route('/get_all_propositions')
def get_all_propositions():
    propositions = []
    for item in Proposicao.objects:
        propositions.append(item.to_json())

    return jsonify(propositions)


@api.route('/update_tweets_propositions')
def update_tweets_propositions():
    
    for item in Proposicao.objects:
        tweets_list = tweets_by_proposition_id(int(item.proposicao_id))
        
        for tweet in tweets_list:
            if "RT " in tweet["text"]:
                continue
                
            PropositionTweet(
                tweet_id = str(tweet["id"]),
                author_id = tweet["author_id"],
                proposition_id = item.proposicao_id,
                date = datetime.strptime(str(tweet["created_at"][0:18]), '%Y-%m-%dT%H:%M:%S') if tweet["created_at"] is not None else None,
                source = tweet["text"]
            ).save()

    return "Done"

@api.route('/get_all_tweets_propositions')
def get_all_tweets_propositions():
    all = []
    for item in PropositionTweet.objects:
        all.append(item.to_json())

    return jsonify(all)

@api.route('/get_tweets_by_proposition_id/<id>')
def get_tweets_by_proposition_id(id):
    tweets = []
    for item in PropositionTweet.objects:
        if int(item.proposition_id) == int(id):
            tweets.append(item.to_json())

    return jsonify(tweets)

@api.route('/delete_all_tweets_propositions')
def delete_all_tweets_propositions():
    PropositionTweet.objects.all().delete()
    return "All propositions tweets were deleted"

def tweets_by_proposition_id(id):
    proposition = {}

    for item in Proposicao.objects:
        if int(item.proposicao_id) == int(id):
            proposition = item.to_json()
            break

    if proposition == {}:
        return {}

    proposition_tweets = []
    
    proposition_number = str(proposition["numero"]) + "/" + str(proposition["ano"])
    key = proposition["sigla_tipo"].replace(" ", "_") + "_" + proposition_number

    params = get_params_2()
    r = requests.get(f'https://api.twitter.com/2/tweets/search/recent?query={key}&max_results=100', headers=auth_header, params=params)
    
    if not r:
        return {}
    
    if not "data" in r.json():
        return {}

    return r.json()["data"]
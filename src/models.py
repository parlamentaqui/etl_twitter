from mongoengine import *

class Deputy(Document):
    id = IntField(primary_key=True)
    name = StringField(required=True)
    photo_url = StringField()
    initial_legislature_id = IntField(required=True)
    final_legislature_id = IntField()
    initial_legislature_year = IntField(required=True)
    final_legislature_year = IntField()
    last_activity_date = DateTimeField()
    full_name = StringField()
    sex = StringField()
    email = StringField()
    birth_date = DateTimeField()
    death_date = DateTimeField()
    federative_unity = StringField()
    party = StringField()
    instagram_username = StringField()
    twitter_username = StringField()
    facebook_username = StringField()
    twitter_id = StringField()
    website = StringField()

    def to_json(self):
        return{
            'id':self.id,
            'name':self.name,
            'photo_url':self.photo_url,
            'initial_legislature_id':self.initial_legislature_id,
            'final_legislature_id':self.final_legislature_id,
            'initial_legislature_year':self.initial_legislature_year,
            'final_legislature_year':self.final_legislature_year,
            'last_activity_date':self.last_activity_date,
            'full_name':self.full_name,
            'sex':self.sex,
            'email':self.email,
            'birth_date':self.birth_date,
            'death_date':self.death_date,
            'federative_unity':self.federative_unity,
            'party':self.party,
            'instagram_username':self.instagram_username,
            'twitter_username':self.twitter_username,
            'facebook_username':self.facebook_username,
            'twitter_id':self.twitter_id,
            'website':self.website
        }


# class News(Document):
#     id = IntField(primary_key=True)
#     deputy_id = IntField()
#     link = StringField()
#     photo = StringField()
#     title = StringField()
#     abstract = StringField()
#     deputy_name = StringField()
#     update_date = DateTimeField()
#     source = StringField()

class DBTest(Document):
    message = StringField()

class Tweet(Document):
    tweet_id = StringField(primary_key=True)
    deputy_id = IntField()
    name = StringField()
    twitter_username = StringField()
    date = DateTimeField()
    source = StringField()

    def to_json(self):
        return {
            'tweet_id':self.tweet_id,
            'deputy_id':self.deputy_id,
            'name':self.name,
            'twitter_username':self.twitter_username,
            'date':self.date,
            'source':self.source
        }

class PropositionTweet(Document):
    tweet_id = StringField(primary_key=True)
    author_id = StringField()
    proposition_id = IntField()
    date = DateTimeField()
    source = StringField()

    def to_json(self):
        return {
            'tweet_id':self.tweet_id,
            'author_id':self.author_id,
            'date':self.date,
            'proposition_id':self.proposition_id,
            'source':self.source
        }

class Proposicao(Document):
    proposicao_id = IntField(primary_key=True)
    id_deputado_autor = IntField(required=True)
    uri = StringField()
    descricao_tipo = StringField()
    ementa = StringField(required=True)
    ementa_detalhada = StringField()
    keywords = StringField()
    data_apresentacao = DateTimeField()
    urlAutor = StringField()
    tipoAutor = StringField()
    nome_autor = StringField()
    sigla_UF_autor = StringField()
    tema_proposicao = StringField()
    sigla_orgao = StringField() # Comeca aqui as informacoes do objeto de status
    data_proposicao = DateTimeField() 
    descricao_situacao = StringField()
    despacho = StringField()
    uri_relator = StringField()
    sigla_tipo = StringField()
    cod_tipo = IntField()
    numero = IntField()
    ano = IntField()
        
    def to_json(self):
        return{
            'proposicao_id': self.proposicao_id,
            'id_deputado_autor': self.id_deputado_autor,
            'uri': self.uri,
            'descricao_tipo': self.descricao_tipo,
            'ementa': self.ementa,
            'ementa_detalhada': self.ementa_detalhada,
            'keywords': self.keywords,
            'urlAutor': self.urlAutor,
            'tipoAutor': self.tipoAutor,
            'nome_autor': self.nome_autor,
            'sigla_UF_autor': self.sigla_UF_autor,
            'tema_proposicao': self.tema_proposicao,
            'sigla_orgao': self.sigla_orgao,
            'data_proposicao': self.data_proposicao,
            'descricao_situacao': self.descricao_situacao,
            'despacho': self.despacho,
            'uri_relator': self.uri_relator,
            'sigla_tipo' : self.sigla_tipo,
            'cod_tipo' : self.cod_tipo,
            'numero' : self.numero,
            'ano' : self.ano
        }
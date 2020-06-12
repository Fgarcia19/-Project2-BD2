# -*- coding: utf-8 -*-
# coding=utf-8
import nltk
from nltk.stem import PorterStemmer
from nltk.stem.snowball import SnowballStemmer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import json
import codecs
from nltk.tokenize import sent_tokenize
from nltk.tokenize import word_tokenize
import operator
import math
import cmath
import re, string, unicodedata
import nltk
import operator
import contractions
import inflect
from bs4 import BeautifulSoup
from nltk import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import LancasterStemmer, WordNetLemmatizer
import io
import tkinter as tk
from tkinter import ttk
import os.path as path
from os import remove

df={}
df_puestas=[]
total_documentos=0
tweets={}

###VARIABLES GLOBALES###
stop_words = set(stopwords.words("spanish")) #lista de stop_words
spanishStemmer=SnowballStemmer("spanish", ignore_stopwords=True) #Stem en español


###INICIO DE FUNCIONES PARA NORMALIZACION###
def remove_non_ascii(words):
    """Remove non-ASCII characters from list of tokenized words"""
    new_words = []
    for word in words:
        new_word = unicodedata.normalize('NFKD', word).encode('ascii', 'ignore').decode('utf-8', 'ignore')
        new_words.append(new_word)
    return new_words

def to_lowercase(words):
    """Convert all characters to lowercase from list of tokenized words"""
    new_words = []
    for word in words:
        new_word = word.lower()
        new_words.append(new_word)
    return new_words

def remove_punctuation(words):
    """Remove punctuation from list of tokenized words"""
    new_words = []
    for word in words:
        new_word = re.sub(r'[^\w\s]', '', word)
        if new_word != '':
            new_words.append(new_word)
    return new_words

def replace_numbers(words):
    """Replace all interger occurrences in list of tokenized words with textual representation"""
    p = inflect.engine()
    new_words = []
    for word in words:
        if word.isdigit():
            new_word = p.number_to_words(word)
            new_words.append(new_word)
        else:
            new_words.append(word)
    return new_words

def remove_stopwords(words):
    """Remove stop words from list of tokenized words"""
    new_words = []
    for word in words:
        if word not in stopwords.words('spanish'):
            new_words.append(word)
    return new_words

def stem_words(words):
    """Stem words in list of tokenized words"""
   # stemmer = LancasterStemmer()
    stemmer=SnowballStemmer("spanish", ignore_stopwords=True)
    stems = []
    for word in words:
        stem = stemmer.stem(word)
        stems.append(stem)
    return stems

def lemmatize_verbs(words):
    """Lemmatize verbs in list of tokenized words"""
    lemmatizer = WordNetLemmatizer()
    lemmas = []
    for word in words:
        lemma = lemmatizer.lemmatize(word, pos='v')
        lemmas.append(lemma)
    return lemmas

def normalize(words):
    words = remove_non_ascii(words)
    words = to_lowercase(words)
    words = remove_punctuation(words)
    words = replace_numbers(words)
    words = remove_stopwords(words)
    return words

def stem_and_lemmatize(words):
    stems = stem_words(words)
    lemmas = lemmatize_verbs(words)
    return stems, lemmas

##FIN DE FUNCIONES PARA NORMALIZACION

def new_last_block():
    ##FUNCION USADA CUANDO UN BLOQUE SOBREPASA LA CANITDAD DE PALABRAS FIJADA POR LO QUE TENGO UNA REFERENCIA DE CUAL ES EL ULTIMO BLOQUE"
    with open("last_indice.txt", errors='ignore', encoding='utf8') as contenido:
        last_indice = contenido.readline()
    li = open("last_indice.txt", 'w')
    n_last_indice = int(last_indice)
    li.write(str(n_last_indice + 1))
    li.close()

def actual_block():
    ##RETORNA EL BLOQUE ACTUAL DEL INDICE INVERTIDO""
    with open("last_indice.txt", errors='ignore', encoding='utf8') as contenido:
        last_indice = contenido.readline()
    return last_indice

def sum_N(num):
    ##AUMENTAR LA CANTIDAD DE DOCUMENTOS DE LA COLECCION##
    with open("N.txt", errors='ignore', encoding='utf8') as contenido:
        last_M = contenido.readline()
    li = open("N.txt", 'w')
    n_last_M = int(last_M)
    li.write(str(n_last_M +num))
    li.close()

def N():
    ##LEER Y RETORNAR LA CANTIDAD DE DOCUMENTOS DE LA COLECCION##
    with open("N.txt", errors='ignore', encoding='utf8') as contenido:
        last_indice = contenido.readline()
    return int(last_indice)



def cargar_datos(ruta):
    ##DADO UN ARCHIVO DE TWEETS UBICADOS EN RUTA, LOS CARGA A BLOQUES DE INDICE INVERTIDO#
    indice_invertido={}
    with open(ruta,errors='ignore',encoding='utf8') as contenido:
        datos = json.load(contenido)
        block=actual_block()
        if path.exists(block+".json"):
            indice=open(block+".json", errors='ignore', encoding='utf8')
            indice_invertido = json.load(indice)
            indice.close()
            remove(block+".json")
        print(len(indice_invertido))
        sum_N(len(datos))
        for i in datos:
            texto=i.get('text')
            words = nltk.word_tokenize(texto)
            words = normalize(words)
            stems, lemmas = stem_and_lemmatize(words)
            for j in stems:
                if j in indice_invertido:
                    indice_invertido[j][0]+=1
                else:
                    if(len(indice_invertido)==10000):
                        f = open(block + ".json", 'w', errors='ignore', encoding='utf8')
                        json.dump(indice_invertido, f)
                        f.close()
                        new_last_block()
                        block=actual_block()
                        indice_invertido={}
                    indice_invertido[j]=[1,{}]
                indice_invertido[j][1][i.get('id')]=stems.count(j)

        final=open(block + ".json", 'w', errors='ignore', encoding='utf8')
        json.dump(indice_invertido, final)
        final.close()
        print(len(indice_invertido))

def tf_idf(tf,df):
    #FORMULA DE TF-IDF
    n=N()
    return math.log10(1+tf)*math.log10(n/df)

def consulta(texto):
    ##Cargar los valor tf y df para aplicar score##
    df={}
    tf={}
    tf_con={}
    words = nltk.word_tokenize(texto)
    words = normalize(words)
    stems, lemmas = stem_and_lemmatize(words)
    for i in stems:
        tf_con[i]=stems.count(i)
        df[i]=0
    print(stems)
    actual=int(actual_block())
    ##VOY BUSCANDO EN LOS BLOQUES CREADOS, LOS KEYWORDS DE LA CONSULTA Y VOY GUARDANDO LOS TF Y DF DE CADA TERMNO PARA LA FORMULA#
    for i in range(0,actual+1):
        archivo=open(str(i)+'.json','r',errors='ignore', encoding='utf8')
        indice_parcial = json.load(archivo)
        for j in stems:
            if j in indice_parcial:
                df[j]+=len(indice_parcial[j][1])
                for k in indice_parcial[j][1]:
                    if k in tf:
                        tf[k][j]=indice_parcial[j][1][k]
                    else:
                        tf[k]={}
                        tf[k][j]=indice_parcial[j][1][k]

    print(df)
    print(tf)
    ##YA TENGO LOS VALORES
    ##YA JU
    scores={}

    ##APLICO SCORE PARA CADA DOCUMENTO
    for i in tf:
        #Numerador
        num=0
        mod_q=0
        mod_d=0
        for j in tf[i]:
            num+=tf_idf(tf[i][j],df[j])*tf_idf(tf_con[j],df[j])
            mod_q+=tf_idf(tf_con[j],df[j])**2
            mod_d += tf_idf(tf[i][j],df[j])**2
        mod_q=mod_q**(0.5)
        mod_d=mod_d**(0.5)
        scores[i]=(num/(mod_d*mod_q))

    ##ORDENO SCORE DE MENOR A MAYOR
    scores_sort = sorted(scores.items(), key=operator.itemgetter(1), reverse=False)
    max=0
    i_t = open("indice_textos.txt", 'r', errors='ignore', encoding='utf8')
    posi=json.load(i_t)
    te = open("textos.txt", 'r', errors='ignore', encoding='utf8')
    respuesta=[]
    ##RETORNO TOP 10 DE LOS VALORES
    for name in enumerate(scores_sort):
        if(max==10):
            break;
        te.seek(posi[name[1][0]])
        linea=te.readline()
        # print(linea)
        respuesta.append(linea)
        print(name[1][0], 'with value', scores[name[1][0]])
        max+=1
    return respuesta

##Fue usado para guardar las relaciones entre los ids y su contenido para poder mostrar los textos al final de la consulta
# t=open("textos.txt",'w', errors='ignore', encoding='utf8')
# p=open("indice_textos.txt",'w', errors='ignore', encoding='utf8')
# pos = {}
#
# def save(indice):
#     for i in indice:
#         pos[i.get('id')] = t.tell()
#         t.write(i.get('user_name'))
#         t.write(" : ")
#         t.write(i.get('text'))
#         t.write("\n")


##PARA EL FRONT
class Application(ttk.Frame):
    def __init__(self, main_window,num,r):
        super().__init__(main_window)
        main_window.geometry("400x500")
#        self.text = tk.StringVar(value=(r[num]))
        char_list = [r[num][j] for j in range(len(r[num])) if ord(r[num][j]) in range(65536)]
        tweet = ''
        for j in char_list:
            tweet = tweet + j
        self.text=tk.StringVar()
        self.text.set(tweet)
        self.label2 = tk.Label(self, textvariable=self.text,bg='light goldenrod')
        self.grid_columnconfigure(1, weight=1)
        self.label2.grid(column=1, row=0, pady=2, padx=10,  sticky="nswe",)
        self.label2.bind( "<Configure>", self.on_label_resize)


    def on_label_resize(self,  event):
        event.widget["wraplength"] = event.width


##FUNCION LLAMADA DESDE EL BOTON DEL FRONT, QUE HARA LA CONSULTA CON LO ESCRITO EN LA CASIILLA DE ENTRADA
def hello():
    consu = entrada1.get()
    print(consu)
    r = consulta(consu)
    ##PARA LOS CASSILLOS QUE SE EDITAN SOLOS
    # for i in range(0,len(r)):
    #     l_var[i].set(r[i])

    ##PARA LOS CASILLOS QUE SE VEN BIEN
    for i in range(0, len(r)):
        app=Application(root,i,r)
        app.pack(expand=True, fill='both')




if __name__ == "__main__":
    root = tk.Tk()
    root.configure(background='steelblue')
    e1 = tk.Label(root, text='Consulta', bg='salmon', fg='white')
    e1.pack(padx=6, pady=4, ipadx=5, ipady=5, fill=tk.X)
    entrada1 = tk.Entry(root)
    entrada1.pack(padx=5, pady=5, ipadx=5, ipady=5,fill=tk.X)
    boton = tk.Button(root, text='Buscar', fg="blue", command=hello)
    boton.pack(side=tk.TOP)


    ##Descomentar para casillos que se cambian solos
    # var = tk.StringVar()
    # var2 = tk.StringVar()
    # var3 = tk.StringVar()
    # var4 = tk.StringVar()
    # var5 = tk.StringVar()
    # var6 = tk.StringVar()
    # var7 = tk.StringVar()
    # var8 = tk.StringVar()
    # var9 = tk.StringVar()
    # var10 = tk.StringVar()
    # l_var = [var, var2, var3, var4, var5, var6, var7, var8, var9, var10]
    # resultado = tk.Label(root, textvariable=var, padx=5, pady=5, width=50)
    # resultado.pack(padx=6, pady=4, ipadx=5, ipady=5, fill=tk.X)
    # resultado2 = tk.Label(root, textvariable=var2, padx=5, pady=5, width=50)
    # resultado2.pack(padx=6, pady=4, ipadx=5, ipady=5, fill=tk.X)
    # resultado3 = tk.Label(root, textvariable=var3, padx=5, pady=5, width=50)
    # resultado3.pack(padx=6, pady=4, ipadx=5, ipady=5, fill=tk.X)
    # resultado4 = tk.Label(root, textvariable=var4, padx=5, pady=5, width=50)
    # resultado4.pack(padx=6, pady=4, ipadx=5, ipady=5, fill=tk.X)
    # resultado5 = tk.Label(root, textvariable=var5, padx=5, pady=5, width=50)
    # resultado5.pack(padx=6, pady=4, ipadx=5, ipady=5, fill=tk.X)
    # resultado6 = tk.Label(root, textvariable=var6, padx=5, pady=5, width=50)
    # resultado6.pack(padx=6, pady=4, ipadx=5, ipady=5, fill=tk.X)
    # resultado7 = tk.Label(root, textvariable=var7, padx=5, pady=5, width=50)
    # resultado7.pack(padx=6, pady=4, ipadx=5, ipady=5, fill=tk.X)
    # resultado8 = tk.Label(root, textvariable=var8, padx=5, pady=5, width=50)
    # resultado8.pack(padx=6, pady=4, ipadx=5, ipady=5, fill=tk.X)
    # resultado9 = tk.Label(root, textvariable=var9, padx=5, pady=5, width=50)
    # resultado9.pack(padx=6, pady=4, ipadx=5, ipady=5, fill=tk.X)
    # resultado10 = tk.Label(root, textvariable=var10, padx=5, pady=5, width=50)
    # resultado10.pack(padx=6, pady=4, ipadx=5, ipady=5, fill=tk.X)

    root.mainloop()





















    ##CARGAR##
    # for i in range(7,10):
    #     with open("clean/tweets_2018-08-0"+str(i)+".json", errors='ignore', encoding='utf8') as contenido:
    #         indice_invertido = json.load(contenido)
    #         save(indice_invertido)
    # for i in range(0,10):
    #     with open("clean/tweets_2018-08-1"+str(i)+".json", errors='ignore', encoding='utf8') as contenido:
    #         indice_invertido = json.load(contenido)
    #         save(indice_invertido)
    # for i in range(0,10):
    #     with open("clean/tweets_2018-08-2"+str(i)+".json", errors='ignore', encoding='utf8') as contenido:
    #         indice_invertido = json.load(contenido)
    #         save(indice_invertido)
    # with open("clean/tweets_2018-08-30.json", errors='ignore', encoding='utf8') as contenido:
    #     indice_invertido = json.load(contenido)
    #     save(indice_invertido)
    # with open("clean/tweets_2018-08-31.json", errors='ignore', encoding='utf8') as contenido:
    #     indice_invertido = json.load(contenido)
    #     save(indice_invertido)
    # with open("clean/tweets_2018-08-31.json", errors='ignore', encoding='utf8') as contenido:
    #     indice_invertido = json.load(contenido)
    #     save(indice_invertido)
    # for i in range(2,10):
    #     with open("clean/tweets_2018-09-0"+str(i)+".json", errors='ignore', encoding='utf8') as contenido:
    #         indice_invertido = json.load(contenido)
    #         save(indice_invertido)
    # for i in range(0,10):
    #     with open("clean/tweets_2018-09-1"+str(i)+".json", errors='ignore', encoding='utf8') as contenido:
    #         indice_invertido = json.load(contenido)
    #         save(indice_invertido)
    # for i in range(0,10):
    #     with open("clean/tweets_2018-09-2"+str(i)+".json", errors='ignore', encoding='utf8') as contenido:
    #         indice_invertido = json.load(contenido)
    #         save(indice_invertido)
    # with open("clean/tweets_2018-09-30.json", errors='ignore', encoding='utf8') as contenido:
    #     indice_invertido = json.load(contenido)
    #     save(indice_invertido)
    # for i in range(1, 6):
    #     with open("clean/tweets_2018-10-0" + str(i) + ".json", errors='ignore', encoding='utf8') as contenido:
    #         indice_invertido = json.load(contenido)
    #         save(indice_invertido)
    # json.dump(pos, p)

    # print(N)
    # lista=[]
    # hola=0
    # actual=int(actual_block())
    # for i in range(0,actual+1):
    #     archivo=open(str(i)+'.json','r',errors='ignore', encoding='utf8')
    #     indice_parcial = json.load(archivo)
    #     for j in indice_parcial:
    #         for k in indice_parcial[j][1]:
    #             if k in lista:
    #                 hola=1
    #             else:
    #                 lista.append(k)
    # print(lista)
    # print(len(lista))







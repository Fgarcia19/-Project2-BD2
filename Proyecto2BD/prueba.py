
import json

with open("docs.txt", errors='ignore', encoding='utf8') as contenido:
    cursos=contenido.readline()
    print(cursos)
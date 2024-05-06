import io
import re
import csv
import time
import nltk
import PyPDF2
import requests
from datetime import datetime
from nltk.tokenize import sent_tokenize
from concurrent.futures import ThreadPoolExecutor, as_completed

def read_pdf_from_url(url):
    response = requests.get(url)
    if response.status_code == 200:
        with io.BytesIO(response.content) as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = []
            for page in pdf_reader.pages:
                text.append(page.extract_text())
            return text
    else:
        return "Failed to retrieve the PDF."

def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'\s+', ' ', text)
    return text

def check_verdict(text):
    
    # nltk.download('punkt')

    positive_keywords = [
        'julgo procedente', 'julgo parcialmente procedente', 'julgo parcialmente procedentes', 'deferida a tutela',
        'concedo a antecipação', 'concedo a segurança', 'concedo o pedido',
        'concedo a medida', 'acolho o pedido', 'declarar a nulidade', 'condenar o réu',
        'procedente em parte', 'concedo parcialmente', 'decido pela procedência',
        'acolher a ação', 'deferimento do pedido', 'satisfazer a demanda', 'aceito integralmente'
    ]

    negative_keywords = [
        'julgo improcedente', 'rejeito a ação', 'rejeito o pedido',
        'indeferimento do pedido', 'pedido improcedente', 'negar a segurança',
        'negar provimento', 'desacolher a ação', 'indeferido o pedido',
        'inadmito a ação', 'nega-se seguimento', 'extingo sem resolução',
        'julgo totalmente improcedente', 'rejeito integralmente', 'extingo o processo',
        'denego a segurança', 'não procede a demanda'
    ]

    sentences = sent_tokenize(text)

    positive_matches = any(re.search(keyword, sentence) for sentence in sentences for keyword in positive_keywords)
    negative_matches = any(re.search(keyword, sentence) for sentence in sentences for keyword in negative_keywords)

    if positive_matches and not negative_matches:
        return "Ganho"
    elif negative_matches and not positive_matches:
        return "Perdido"
    elif positive_matches and negative_matches:
        return "Parcialmente Ganho"
    else:
        return "Indeterminado"


def getVeredicts(sentencas):    
    vereditos = []
    for sentenca in sentencas:
        text = read_pdf_from_url(sentenca['link'])
        text_normalized = preprocess_text(" ".join(text))
        veredito_string = check_verdict(text_normalized)
        vereditos.append(veredito_string)
      
    return vereditos

def getPdfUrls(id):
    cleanProcessId = re.sub(r'\D', '', id)
    url = f'https://esb.tjpb.jus.br/cp-backend/sistemas/3/processos/{cleanProcessId}/documentos'
    pdf_urls = requests.get(url)  
    sentencas = [item for item in pdf_urls.json() if item['descricao'] == 'Sentença']

    if(len(sentencas) == 0):
        return{'first': "Nenhuma Sentença", 'all': "-", 'total': "-"}

    sentencas_ordenadas = sorted(sentencas, key=lambda x: datetime.strptime(x['data'], "%Y-%m-%dT%H:%M:%S.%fZ"))
    vereditos = getVeredicts(sentencas_ordenadas)

    return {'first': vereditos[0], 'all': " | ".join(vereditos), 'total': len(vereditos)}

def main():
    total_linhas = sum(1 for linha in open('dataset/ids_processos.csv', 'r')) - 1 
    with open('dataset/ids_processos.csv', 'r') as file:
        reader = csv.reader(file)
        processos_ids = [line.strip() for line in file if line.strip()]

    num_threads = min(10, len(processos_ids))

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        future_to_id = {executor.submit(getPdfUrls, processo_id): processo_id for processo_id in processos_ids}

        with open('resultados.csv', 'w', newline='') as csvfile:
            fieldnames = ['Processo_ID', 'Primeiro Resultado', 'Todos os Resultados', 'Total Vereditos']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            linhas_processadas = 0
            for future in as_completed(future_to_id):
                processo_id = re.sub(r'\D', '', future_to_id[future]) 
                try:
                    data = future.result()
                    writer.writerow({'Processo_ID': processo_id, 'Primeiro Resultado': data['first'], 'Todos os Resultados': data['all'], 'Total Vereditos': data['total']})
                    linhas_processadas += 1
                    
                except Exception as e:
                    print(e)
                    writer.writerow({'Processo_ID': processo_id, 'Primeiro Resultado': "Falha", 'Todos os Resultados': "", 'Total Vereditos': ''})
                    time.sleep(5)
                    linhas_processadas += 1
                
                porcentagem = (linhas_processadas / total_linhas) * 100
                progresso = int(porcentagem / 5) 
                print(f"\r[{'#' * progresso}{' ' * (20 - progresso)}] {linhas_processadas}/{total_linhas } ({porcentagem:.2f}%)", end='', flush=True)
            

if __name__ == "__main__":
    main()

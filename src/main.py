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

    positive_regex = [
        r"julg\w*\s+procedente\w*",
        r"decid\w*\s+procedente\w*", 
        r"pela\s+procedência", 
        r"totalmente\s+procedente",
        r"parcialmente\s+procedente",
        r"acolho\s+o\s+pedido\s+cautelar"
    ]
    negative_regex = [
        r"julg\w*\s+improcedente\w*",
        r"decid\w*\s+improcedente\w*",  
        r"pela\s+improcedência",       
        r"rejeita-se\w*\s*o\s+pedido",       
        r"(liminarmente|totalmente)\s+improcedente"  
    ]

    acordo_regex = r"homolog\w*"

    extinct_regex = [
        r"sem\s+.*?\s+d.*?\s+mérito", 
        r"julg\w*\s+extinto",
    ]

    partial_regex = [
        r"parcialmente\s+procedente", 
        r"procedente\s+em\s+parte"
    ]

    sentences = sent_tokenize(text)

    positive_matches = any(re.search(regex, sentence, re.IGNORECASE) for sentence in sentences for regex in positive_regex)
    negative_matches = any(re.search(regex, sentence, re.IGNORECASE) for sentence in sentences for regex in negative_regex)
    acordo_matches = any(re.search(acordo_regex, sentence, re.IGNORECASE) for sentence in sentences)
    extinct_matches = any(re.search(regex, sentence, re.IGNORECASE) for sentence in sentences for regex in extinct_regex)
    partial_matches = any(re.search(regex, sentence, re.IGNORECASE) for sentence in sentences for regex in partial_regex)

    # matches = ""

    # if positive_matches: matches += "Houve Ganho "
    # if negative_matches: matches += "Houve Perdido "
    # if acordo_matches: matches += "Houve Acordo "
    # if extinct_matches: matches += "Houve Extinto "
    # if partial_matches: matches += "Houve Ganho Parcial "

    

    if positive_matches and not negative_matches:
        return "Ganho"
    elif negative_matches and not positive_matches:
        return "Perdido"
    elif acordo_matches and not positive_matches and not negative_matches:
        return "Acordo"
    elif partial_matches and not positive_matches and not negative_matches:
        return "Parcialmente Procedente"
    elif extinct_matches and not positive_matches and not negative_matches:
        return "Extinto"
    else:
        return "Outros"


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
    total_linhas = sum(1 for linha in open('dataset/ids_processos_classe7.csv', 'r')) - 1 
    with open('dataset/ids_processos_classe7.csv', 'r') as file:
        reader = csv.reader(file)
        processos_ids = [line.strip() for line in file if line.strip()]

    num_threads = min(10, len(processos_ids))

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        future_to_id = {executor.submit(getPdfUrls, processo_id): processo_id for processo_id in processos_ids}

        with open('resultados_classe7_3.csv', 'w', newline='') as csvfile:
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
                    time.sleep(60)
                    linhas_processadas += 1
                
                porcentagem = (linhas_processadas / total_linhas) * 100
                progresso = int(porcentagem / 5) 
                print(f"\r[{'#' * progresso}{' ' * (20 - progresso)}] {linhas_processadas}/{total_linhas } ({porcentagem:.2f}%)", end='', flush=True)
            

if __name__ == "__main__":
    print(datetime.now())
    main()

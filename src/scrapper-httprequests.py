import csv
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
import re
from tqdm import tqdm
import datetime

def fazer_requisicao(processo_id):
    cleanProcessId = re.sub(r'\D', '', processo_id)
    url = f'https://esb.tjpb.jus.br/cp-backend/sistemas/3/processos/{cleanProcessId}?campos=completo'
    response = requests.get(url)

    return response.json()

def main():
    total_linhas = sum(1 for linha in open('dataset/apenasIds/novo_dataset_processo.csv', 'r'))
    with open('dataset/apenasIds/novo_dataset_processo.csv', 'r') as file:
        reader = csv.reader(file)
        processos_ids = [row[0] for row in reader]

    num_threads = 10


    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        future_to_id = {executor.submit(fazer_requisicao, processo_id): processo_id for processo_id in processos_ids}

        with open('resultados.csv', 'w', newline='') as csvfile:
            fieldnames = ['Processo_ID', 'Resultado']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()


            linhas_processadas = 0
            for future in as_completed(future_to_id):
                processo_id = future_to_id[future]
                try:
                    data = future.result()
                    writer.writerow({'Processo_ID': processo_id, 'Resultado': data["gratuito"]})
                    linhas_processadas += 1
                    
                except Exception as e:
                    print(e)
                    writer.writerow({'Processo_ID': processo_id, 'Resultado': "Falha"})
                    linhas_processadas += 1
                
                porcentagem = (linhas_processadas / total_linhas) * 100
                progresso = int(porcentagem / 5) 
                print(f"\r[{'#' * progresso}{' ' * (20 - progresso)}] {linhas_processadas}/{total_linhas} ({porcentagem:.2f}%)", end='', flush=True)
            

if __name__ == "__main__":
    main()

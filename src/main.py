import requests
import PyPDF2
import io

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

# URL do PDF que você deseja ler

process = 'https://esb.tjpb.jus.br/cp-backend/sistemas/3/processos/08012591420218150601/documentos'
pdf_urls = requests.get(process)
# pdf_text = read_pdf_from_url(pdf_url)
print(pdf_urls.json())
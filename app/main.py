import os
import re
import requests
from flask import Flask, render_template, request
from dotenv import load_dotenv

# .env dosyasından çevre değişkenlerini yükle
load_dotenv()

app = Flask(__name__)

# Ollama API URL'ini çevre değişkeninden al veya varsayılan değeri kullan
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://localhost:11434")

# Job sınıfı örneği
JOB_CLASS = """
class Job:
    def __init__(self, id, name, description):
        self.id = id
        self.name = name
        self.description = description
        
    def execute(self):
        # Base execution method
        pass
"""

def generate_code_with_ollama(prompt):
    """
    Ollama API'sini kullanarak kod üretme
    """
    system_prompt = f"""
    Sen bir kod üretme asistanısın. Kullanıcının isteğine göre Python kodu üretmelisin.
    Kodun, aşağıda verilen Job sınıfını genişleten bir yapıda olmalı.
    
    {JOB_CLASS}
    
    Çıktını şu formatta ver:
    ### BAŞLIK: [Kısa açıklayıcı başlık]
    
    ```python
    [Python kodu buraya]
    ```
    """
    
    try:
        response = requests.post(
            f"{OLLAMA_API_URL}/api/generate",
            json={
                "model": "codellama",  # Code için optimize edilmiş Llama modeli
                "prompt": f"{system_prompt}\n\nKullanıcı İsteği: {prompt}",
                "stream": False
            },
            timeout=60
        )
        
        if response.status_code == 200:
            return response.json()["response"]
        else:
            return f"API Hatası: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Hata oluştu: {str(e)}"

def parse_response(response):
    """
    LLM yanıtından başlık ve kodu ayırma
    """
    # Başlığı bul
    title_match = re.search(r"### BAŞLIK: (.*?)$", response, re.MULTILINE)
    title = title_match.group(1) if title_match else "Oluşturulan Kod"
    
    # Kodu bul
    code_match = re.search(r"```python\n(.*?)```", response, re.DOTALL)
    code = code_match.group(1) if code_match else "Kod bulunamadı."
    
    return title, code

@app.route('/', methods=['GET', 'POST'])
def index():
    title = None
    code = None
    prompt = None
    error = None
    
    if request.method == 'POST':
        prompt = request.form.get('prompt')
        if prompt:
            response = generate_code_with_ollama(prompt)
            if response.startswith("Hata") or response.startswith("API Hatası"):
                error = response
            else:
                title, code = parse_response(response)
    
    return render_template('index.html', title=title, code=code, prompt=prompt, error=error)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

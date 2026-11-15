import re
import requests

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
resp = requests.get("https://lista.mercadolivre.com.br/mouse-gamer-redragon", headers=headers, timeout=10)
# Vamos ver alguns links com href
hrefs = re.findall(r'href="([^"]+)"', resp.text)
ml_links = [h for h in hrefs if "mercadolivre.com.br" in h and "/p/" in h or "-MLB" in h]
print("Hrefs totais:", len(hrefs))
print("Links de produtos com /p/ ou -MLB:", len(ml_links))
if ml_links:
    print("Link direto:", ml_links[0].split("?")[0])

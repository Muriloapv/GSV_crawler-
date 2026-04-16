from playwright.sync_api import sync_playwright
from PIL import Image
import re
import os
import ddddocr
import json
from datetime import datetime

listCpfCnpj = []
url = 'https://www3.prefeitura.sp.gov.br/cadin/Pesq_Deb.aspx'
caminhoCaptcha = r"C:\Temp\captcha.jpg"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
json_cadin = os.path.join(BASE_DIR, "cadin_consulta.json")
json_pesquisa = os.path.join(BASE_DIR, "dados.json")

with open(json_pesquisa, "r", encoding="utf-8") as jsonPesquisa:
    pesquisa_json = json.load(jsonPesquisa)

listCpfCnpj = [item["cpf_cnpj"] for item in pesquisa_json["dados_pesquisa"]]


# Pega a imagem do captcha e trata
def getCaptcha(_captchaImg) -> str:
    _captchaImg.wait_for(state="visible")
    _captchaImg.screenshot(path=caminhoCaptcha)

    imagem = Image.open(caminhoCaptcha)
    largura, altura = imagem.size

    imagem = imagem.resize((largura * 3, altura * 3), Image.LANCZOS)
    imagem = imagem.convert("L")
    imagem.save(caminhoCaptcha)

    returnCaptcha = ler_captcha(caminhoCaptcha)
    print(f"Captcha: '{returnCaptcha}'")
    return returnCaptcha


# OCR do captcha
def ler_captcha(caminho: str) -> str:
    ocr = ddddocr.DdddOcr(show_ad=False)

    with open(caminho, "rb") as f:
        imagem_bytes = f.read()

    texto = ocr.classification(imagem_bytes)
    return re.sub(r'[^A-Za-z0-9]', '', texto).upper()


def inputCaptcha(pagina) -> str:
    pagina.wait_for_timeout(3000)
    pagina.mouse.move(200, 300)

    captchaImg = pagina.get_by_role("img", name="Informe os caracteres da")
    textoCaptcha = getCaptcha(captchaImg)
    return textoCaptcha


with sync_playwright() as pw:
    navegador = pw.chromium.launch_persistent_context(
        user_data_dir=r'C:\Temp\pw_profile',
        headless=False,
        channel="chrome",
        ignore_default_args=["--enable-automation"],
        args=[
            "--disable-blink-features=AutomationControlled",
            "--start-maximized",
            "--no-sandbox",
        ]
    )

    pagina = navegador.new_page()
    print(f'Acessando: {url}')

    dados_json = {
        "pagina": "CADIN Municipal - Consulta Inscritos",
        "url": url,
        "resultConsulta": [],
        "consultado_em": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    for index, cpfCnpj in enumerate(listCpfCnpj, start=1):
        pagina.goto(url)
        pagina.wait_for_timeout(3000)
        pagina.mouse.move(200, 300)

        btnCookies = pagina.get_by_role("tab", name="Autorizo o uso de todos os")
        if btnCookies.count() > 0:
            btnCookies.click()

        campoCpf = pagina.get_by_role("textbox", name="CNPJ ou CPF.")
        campoCpf.fill("")
        campoCpf.type(cpfCnpj, delay=120)

        resultPesquisa = ""

        for tentativa in range(1, 4):
            textoCaptcha = inputCaptcha(pagina)

            campoCaptcha = pagina.get_by_role("textbox", name="Informe os caracteres da")
            campoCaptcha.fill("")
            campoCaptcha.type(textoCaptcha, delay=120)

            pagina.wait_for_timeout(800)
            pagina.mouse.move(300, 400)

            pagina.get_by_role("button", name="Pesquisar").click()
            pagina.wait_for_timeout(2000)

            locator = pagina.locator("span#lbl_NaoAchou")

            if locator.count() > 0:
                texto = locator.inner_text().strip()

                if texto:
                    resultPesquisa = texto
                    break
            else:
                resultPesquisa = "FORAM ENCONTRADAS PENDÊNCIAS!"
                break

        else:
            resultPesquisa = "Erro ao validar captcha após várias tentativas"

        print(f"[{cpfCnpj}] → {resultPesquisa}")

        dados_json["resultConsulta"].append({
            "consulta": index,
            "cpf_cnpj": cpfCnpj,
            "retorno": resultPesquisa,
        })

    with open(json_cadin, 'w', encoding='utf-8') as jsonSave:
        json.dump(dados_json, jsonSave, ensure_ascii=False, indent=4)

    print("JSON salvo com sucesso.")
    pagina.wait_for_timeout(5000)
    navegador.close()
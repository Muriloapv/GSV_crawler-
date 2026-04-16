from playwright.sync_api import sync_playwright
from PIL import Image
import re
import os
import ddddocr
import json
from datetime import datetime

cpfCnpj        = '11462916988'
url            = 'https://www3.prefeitura.sp.gov.br/cadin/Pesq_Deb.aspx' 
caminhoCaptcha = r"C:\Temp\captcha.jpg"
   
#Pega a imagem do captcha e a trata
def getCaptcha( _captchaImg ) -> str:
   _captchaImg.wait_for( state="visible" )
   _captchaImg.screenshot( path=caminhoCaptcha )

   imagem          = Image.open(caminhoCaptcha)
   largura, altura = imagem.size

   imagem          = imagem.resize((largura * 3, altura * 3), Image.LANCZOS)
   imagem          = imagem.convert("L")
   imagem.save(caminhoCaptcha)
    
   returnCaptcha   = ler_captcha(caminhoCaptcha)
   print( f"Captacha: '{returnCaptcha}'" )
   return returnCaptcha 

#Faz a leitura do captcha de img para texto
def ler_captcha( caminho: str ) -> str:
   ocr = ddddocr.DdddOcr( show_ad=False )

   with open(caminho, "rb") as f:
      imagem_bytes = f.read()

   texto = ocr.classification(imagem_bytes)
   return re.sub(r'[^A-Za-z0-9]', '', texto).upper()
   
with sync_playwright() as pw:
    navegador   = pw.chromium.launch_persistent_context(
        user_data_dir=r'C:\Temp\pw_profile',
        headless=False,#alterar para true caso não queira que abra a aba
        channel="chrome", 
        ignore_default_args=["--enable-automation"], 
        args=[
            "--disable-blink-features=AutomationControlled",
            "--start-maximized",
            "--no-sandbox",
        ]
    )   
    pagina = navegador.new_page()
    pagina.goto( url )
    pagina.wait_for_timeout(3000)
    pagina.mouse.move(200, 300)

    paginaTitle = pagina.title()
    captchaImg  = pagina.get_by_role("img", name="Informe os caracteres da")

    btnCookies  = pagina.get_by_role("tab", name="Autorizo o uso de todos os")
    if btnCookies.count() > 0:
        btnCookies.click()#avaliar negar

    textoCaptcha = getCaptcha(captchaImg)
    pagina.get_by_role("textbox", name="CNPJ ou CPF.").click()
    pagina.wait_for_timeout(500)
    pagina.get_by_role("textbox", name="CNPJ ou CPF.").type( cpfCnpj, delay=120 )
    pagina.wait_for_timeout(800)
    pagina.mouse.move(300, 400)

    pagina.get_by_role("textbox", name="Informe os caracteres da").click()
    pagina.get_by_role("textbox", name="Informe os caracteres da").type( textoCaptcha, delay=120)

    pagina.wait_for_timeout(800)
    pagina.mouse.move(300, 400)  
    
    pagina.get_by_role("button", name="Pesquisar").click()
    BASE_DIR       = os.path.dirname(os.path.abspath(__file__))
    json_path      = os.path.join(BASE_DIR, "cadin_consulta.json" )
    resultPesquisa = pagina.inner_text("span#lbl_NaoAchou").strip()
    dados_json = {
        "url"          : url,
        "pagina"       : paginaTitle,
        "cpf_cnpj"     : cpfCnpj,
        "result"       : resultPesquisa,
        "consultado_em": datetime.now().strftime("%Y-%m-%d %H:%M:%S")    
    }

    with open( json_path, 'w', encoding='utf-8') as f:
        json.dump( dados_json, f, ensure_ascii=False, indent=4)
    
    print(paginaTitle)
    print(resultPesquisa)
    print("JSON Salvo com sucesso.")
    pagina.wait_for_timeout(5000)
    navegador.close()
    




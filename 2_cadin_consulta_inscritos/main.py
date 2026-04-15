from playwright.sync_api import sync_playwright
from PIL import Image
import re
import os
import ddddocr

listCpfCnpj    = []
cpfCnpj        = '11462916988'
caminhoCaptcha = r"C:\Temp\captcha.jpg"#os.path.join(BASE_DIR, "captcha.png")
   
def getCaptcha( _captchaImg ) -> str:
    _captchaImg.wait_for(state="visible")
    _captchaImg.screenshot( path=caminhoCaptcha )

    imagem          = Image.open(caminhoCaptcha)
    largura, altura = imagem.size

    imagem          = imagem.resize((largura * 3, altura * 3), Image.LANCZOS)
    imagem          = imagem.convert("L")
    imagem.save(caminhoCaptcha)
    
    returnCaptcha   = ler_captcha(caminhoCaptcha)
    print( f"Captacha: '{returnCaptcha}'" )
    return returnCaptcha 

def ler_captcha( caminho: str ) -> str:
    ocr = ddddocr.DdddOcr( show_ad=False )

    with open(caminho, "rb") as f:
       imagem_bytes = f.read()

    texto = ocr.classification(imagem_bytes)
    return re.sub(r'[^A-Za-z0-9]', '', texto).upper()
   
with sync_playwright() as pw:
   # navegador = pw.chromium.launch(headless=False)
    navegador   = pw.chromium.launch_persistent_context(
        user_data_dir=r'C:\Temp\pw_profile',
        headless=False,#alterar para true caso não queira que abra a aba
        channel="chrome", 
        args=[ 
                "--disable-blink-features=AutomationControlled",
                "--disable-infobars",
                "--start-maximized",
                "--no-sandbox", 
            ]
    )   
    pagina = navegador.new_page()
    pagina.goto('https://www3.prefeitura.sp.gov.br/cadin/Pesq_Deb.aspx')
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
    pagina.get_by_role("textbox", name="CNPJ ou CPF.").type( cpfCnpj.upper(), delay=120 )
    pagina.wait_for_timeout(800)
    pagina.mouse.move(300, 400)

    pagina.get_by_role("textbox", name="Informe os caracteres da").click()
    pagina.get_by_role("textbox", name="Informe os caracteres da").type( textoCaptcha, delay=120)

    pagina.wait_for_timeout(800)
    pagina.mouse.move(300, 400)  
    pagina.get_by_role("button", name="Pesquisar").click()

    pagina.wait_for_timeout(10000)
    navegador.close()
    




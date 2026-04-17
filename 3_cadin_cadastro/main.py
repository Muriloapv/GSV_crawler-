from playwright.sync_api import sync_playwright
from PIL import Image
import re
import ddddocr
from datetime import datetime

cpfCnpj        = '11462916988'
nome           = 'Murilo Alves Pereira Varoto'
dtNascimento   = '07/01/2004'
url            = 'https://cadin.prefeitura.sp.gov.br/FiscRecFed.aspx'
caminhoCaptcha = r"C:\Temp\captcha.jpg"
max_tentativas = 3
   
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
   
def inputCaptcha( pagina ) -> str:
   pagina.wait_for_timeout(3000)
   pagina.mouse.move(200, 300)
   
   captchaImg   = pagina.get_by_role("img", name="Imagem")
   textoCaptcha = getCaptcha(captchaImg)
   return textoCaptcha

with sync_playwright() as pw:
   navegador = pw.chromium.launch_persistent_context(
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
   pagina       = navegador.new_page()
   pagina.goto( url )
   paginaTitle  = pagina.title()
   textoCaptcha = inputCaptcha( pagina )

   pagina.get_by_role("textbox", name="CPF. CPF deve ser digitado").type( cpfCnpj, delay=120 )
   pagina.wait_for_timeout(800)
   pagina.get_by_role("textbox", name="Nome. Campo deve ser digitado").type( nome, delay=120 )
   pagina.wait_for_timeout(500)
   pagina.get_by_role("textbox", name="Data de Nascimento. Data deve").type( dtNascimento, delay=120 )
    
   pagina.mouse.move(300, 400)
   campoCaptcha = pagina.locator("#txtwcpSenha")

   campoCaptcha.click()
   campoCaptcha.type(textoCaptcha, delay=120)

   pagina.wait_for_timeout(800)
   pagina.mouse.move(300, 400)     
   pagina.get_by_role("button", name="Login").click()

   if pagina.url == url:
      mensagem = 'Não foi possivel efetuar login'
      for tentativas in range( 1, max_tentativas +1 ):
         textoCaptcha = inputCaptcha( pagina )
         campoCaptcha.fill("")
         campoCaptcha.type(textoCaptcha, delay=120)
         pagina.get_by_role("button", name="Login").click()

         if pagina.url != url:
            mensagem = 'Login efetuado com sucesso'
            break

   print( paginaTitle )
   print( mensagem )
   pagina.wait_for_timeout(5000)
   navegador.close()
  
from playwright.sync_api import sync_playwright
import easyocr
import csv
import json
import os

with sync_playwright() as pw:
   # navegador = pw.chromium.launch(headless=False)
   cpfCnpj     = '11462916988'
   listCpfCnpj = []
   navegador = pw.chromium.launch_persistent_context(
      user_data_dir=r'C:\Temp\pw_profile',
      headless=False,#alterar para true caso não queira que abra a aba
      channel="chrome", 
      args=[ "--disable-blink-features=AutomationControlled",
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
   captchaImg.screenshot( __path__="captcha.png")
   
   reader       = easyocr.Reader(['en'])
   result       = reader.readtext('./2_cadin_consulta_inscritos/captcha.png')
   textoCaptcha = result[0][1]

   btnCookies  = pagina.get_by_role("tab", name="Autorizo o uso de todos os")
   if btnCookies.count() > 0:
      btnCookies.click()#avaliar negar

   # if cpfCnpj != "":
   #    pagina.get_by_role("textbox", name="CNPJ ou CPF.").fill( cpfCnpj )
   # elif len(listCpfCnpj) > 0:
   #    for iCpfCnpj in listCpfCnpj:

   pagina.get_by_role("textbox", name="CNPJ ou CPF.").click()
   pagina.wait_for_timeout(500)
   pagina.get_by_role("textbox", name="CNPJ ou CPF.").type( cpfCnpj, delay=120 )
   pagina.wait_for_timeout(800)
   pagina.mouse.move(300, 400)

   pagina.get_by_role("textbox", name="Informe os caracteres da").click()
   pagina.get_by_role("textbox", name="Informe os caracteres da").type('12asd', delay=120)

   pagina.wait_for_timeout(800)
   pagina.mouse.move(300, 400)  
   pagina.get_by_role("button", name="Pesquisar").click()

   pagina.wait_for_timeout(10000)
   navegador.close()




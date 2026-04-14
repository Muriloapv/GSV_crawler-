from playwright.sync_api import sync_playwright
import csv
import json

with sync_playwright() as pw:
   colunas   = ["CPF/CNPJ", "Nome", "Valor total da dívida (R$)"]
   cpfCnpj   = ""
   nome      = "Murilo"
   valorMin  = "0,00"
   valorMax  = "10.000"
   navegador = pw.chromium.launch_persistent_context(
      user_data_dir=r'C:\Temp\pw_profile',
      headless=False,
      channel="chrome", 
      args=[ "--disable-blink-features=AutomationControlled",
             "--disable-infobars",
             "--start-maximized",
             "--no-sandbox", 
            ]
   )

   pagina = navegador.new_page()
   pagina.goto('https://www.listadevedores.pgfn.gov.br/')

   paginaTitle = pagina.title()
   pagina.wait_for_timeout(3000)
   pagina.mouse.move(200, 300)
   
   if cpfCnpj != "":
      pagina.get_by_role("textbox", name="CPF/CNPJ").fill( cpfCnpj )
   
   pagina.wait_for_timeout(1000)
   if nome != "":
      pagina.get_by_role("textbox", name="Nome").fill( nome )
   
   pagina.wait_for_timeout(1000)   
   if valorMin != "":
      pagina.get_by_role("textbox", name="Valor mínimo").fill( valorMin )
   
   pagina.wait_for_timeout(1000)
   if valorMax != "":
      pagina.get_by_role("textbox", name="Valor máximo").fill( valorMax ) 
   
   pagina.mouse.move(200, 900)
   pagina.wait_for_timeout(1000)

   pagina.get_by_role("button", name="Consultar").click()   
   
   pagina.wait_for_selector("table tbody tr.ng-star-inserted", timeout=15000)
   pagina.wait_for_selector("p.total-mensagens strong", timeout=15000)
   pagina.wait_for_timeout(2000)  # aguarda renderização completa

   total_linhas = pagina.locator("p.total-mensagens strong" ).inner_text()
   linhas       = pagina.locator("table tbody tr.ng-star-inserted").all()
   resultados   = []
   
   print( paginaTitle )
   print( total_linhas + ' Registros')
   total_linhaInt = int(total_linhas.replace(".", ""))

   if total_linhaInt > 0:
      for index, linha in enumerate(linhas):
         celulas = linha.locator("td").all()
         textos  = [ c.inner_text().strip() for c in celulas ]
         print( f"Linha { index + 1 }: {textos}")
         resultados.append(textos)

      with open("regularize.csv", "w", newline="", encoding="utf-8-sig" ) as arquivo:
         writer = csv.writer( arquivo       )
         writer.writerow    ([ paginaTitle ])
         writer.writerow    ([             ])
         writer.writerow    ( colunas       )
         writer.writerows   ( resultados    )   
      
      dados_json = {
         "titulo"    : paginaTitle,
         "total"     : len(resultados),
         "registros" : []
      }

      for linha in resultados:
         dados_json["registros"].append({
            "id"      : linha[0],
            "cpf_cnpj": linha[1],
            "nome"    : linha[2],
            "valor"   : linha[3]
         })
      
      with open( "regularize.json", "w", encoding="utf-8" ) as arquivo:
         json.dump( dados_json, arquivo, ensure_ascii=False, indent=4)
      
      print( f"CSV e Json Salvo com: {len(resultados)} registros")
   else:
      print( "Nenhum registro encontrado!" )   
   navegador.close()

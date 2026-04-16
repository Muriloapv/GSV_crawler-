1. [ Regularize - Lista de devedores ](https://www.listadevedores.pgfn.gov.br/)

```
Executar crawler: python .\1_regularize\main.py
```

2. [ CADIN Municipal - Consulta Inscritos ](https://www3.prefeitura.sp.gov.br/cadin/Pesq_Deb.aspx)

```
Executar crawler: python .\2_cadin_consulta_inscritos\main.py
```

```
Executar crawler: python .\2_cadin_consulta_inscritos\mainList.py
```

3. [ CADASTRO INFORMATIVO MUNICIPAL - CADIN ](https://cadin.prefeitura.sp.gov.br/FiscRecFed.aspx)

```
Executar crawler:  python .\3_cadin_cadastro\main.py
```

## Como usar

1. Clone o repositório:
   ```
   git clone https://github.com/Muriloapv/GSV_crawler-.git
   ```
2. Crie e ative um ambiente virtual:
   ```
   python -m venv venv
   ```
3. Ative o ambiente virtual:
   ```
   .\venv\Scripts\activate
   ```
4. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```

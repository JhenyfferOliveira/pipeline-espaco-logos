import requests
import pandas as pd
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os, json

TOKEN_DE_ACESSO = os.environ.get("TOKEN_DE_ACESSO")
ID_USUARIO_INSTAGRAM = os.environ.get("ID_USUARIO_INSTAGRAM")
GOOGLE_CREDENTIALS_JSON = os.getenv("GOOGLE_CREDENTIALS_JSON")  # conteúdo JSON da chave
NOME_PLANILHA = os.getenv("ong_info_raw")

def buscar_midias_do_usuario():
    url = f"https://graph.facebook.com/v19.0/{ID_USUARIO_INSTAGRAM}/media"
    params = {
        'fields': 'id,caption,media_type,timestamp,permalink,like_count,comments_count',
        'access_token': TOKEN_DE_ACESSO,
        'limit': 100
    }
    todas_midias = []
    while url:
        r = requests.get(url, params=params if not todas_midias else None)
        dados = r.json()
        todas_midias.extend(dados.get('data', []))
        url = dados.get('paging', {}).get('next')
        params = None
    return todas_midias

def salvar_raw_no_sheets(dados):
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name("credenciais.json", scope)
    client = gspread.authorize(creds)

    planilha = client.open(NOME_PLANILHA)

    try:
        aba = planilha.worksheet('raw')
        aba.clear()
    except gspread.WorksheetNotFound:
        aba = planilha.add_worksheet(title='raw', rows='1000', cols='20')

    df = pd.DataFrame(dados)
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    df['timestamp'] = df['timestamp'].dt.strftime('%Y-%m-%d')

    df = df.replace([float('inf'), float('-inf')], 0)
    df = df.fillna(0)

    valores = [df.columns.values.tolist()] + df.values.tolist()
    aba.update(valores)


def main():
    midias = buscar_midias_do_usuario()
    salvar_raw_no_sheets(midias)
    print(f"{len(midias)} posts salvos na aba 'raw' da planilha.")

if __name__ == "__main__":
    main()
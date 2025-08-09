import requests
import pandas as pd
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

TOKEN_DE_ACESSO = "EAAIr3fzAZBE4BPMgZCU1RaojNCbF2qJ0nI3nu5znvXquaqEILEHxKMWlFPqJ7TG8JC9vZBotv90mzZCxC5tn1dPqPYTZCIrBEfRsNcObbhSgKobkgQ9HWKvtLsZBqj7gmB1bxNecolywZCNewPi1rEnWUI1kYPZA2qvTgJLweKqbNLc5edWizjnO3JZCR55uRLJ9ixln0Ccg75P0ZB0ByTycPMB0xy"
ID_USUARIO_INSTAGRAM = "17841403166668009"
GOOGLE_CREDENTIALS_JSON = "credenciais.json"
NOME_PLANILHA = "ong_info_raw"

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
    creds = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_CREDENTIALS_JSON, scope)
    client = gspread.authorize(creds)

    planilha = client.open(NOME_PLANILHA)

    try:
        aba = planilha.worksheet('raw')
        aba.clear()
    except gspread.WorksheetNotFound:
        aba = planilha.add_worksheet(title='raw', rows='1000', cols='20')

    df = pd.DataFrame(dados)
    # Ajuste para timestamp legível
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    valores = [df.columns.values.tolist()] + df.values.tolist()
    aba.update(valores)

def main():
    midias = buscar_midias_do_usuario()
    salvar_raw_no_sheets(midias)
    print(f"{len(midias)} posts salvos na aba 'raw' da planilha.")

if __name__ == "__main__":
    main()

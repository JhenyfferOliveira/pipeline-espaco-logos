import requests, gspread, os
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
INSTAGRAM_USER_ID = os.environ.get("INSTAGRAM_USER_ID")
GOOGLE_CREDENTIALS_JSON = os.getenv("GOOGLE_CREDENTIALS_JSON")
SPREADSHEET_NAME = os.getenv("ong_info_raw")

print("ACCESS_TOKEN:", ACCESS_TOKEN)
print("INSTAGRAM_USER_ID:", INSTAGRAM_USER_ID)

def get_user_media():
    url = f"https://graph.facebook.com/v19.0/{INSTAGRAM_USER_ID}/media"
    params = {
        'fields': 'id,caption,media_type,timestamp,permalink,like_count,comments_count',
        'access_token': ACCESS_TOKEN,
        'limit': 100
    }
    
    all_midia = []
    
    while url:
        r = requests.get(url, params=params if not all_midia else None)
        data = r.json()
        all_midia.extend(data.get('data', []))
        url = data.get('paging', {}).get('next')
        params = None
    
    return all_midia

def save_raw_data_to_sheets(data):
    print(f"Quantidade de itens recebidos: {len(data)}")
    if len(data) > 0:
        print(f"Chaves do primeiro item: {data[0].keys()}")
    else:
        print("Nenhum dado recebido!")

    # Autenticação e planilha
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name("credenciais.json", scope)
    client = gspread.authorize(creds)
    spreadsheet = client.open(SPREADSHEET_NAME)

    try:
        sheet = spreadsheet.worksheet('raw')
        sheet.clear()
    except gspread.WorksheetNotFound:
        sheet = spreadsheet.add_worksheet(title='raw', rows='1000', cols='20')

    # Filtra só os dados com timestamp
    filtered_data = [item for item in data if 'timestamp' in item]
    print(f"Quantidade de itens com 'timestamp': {len(filtered_data)}")

    df = pd.DataFrame(filtered_data)
    print(f"Colunas do DataFrame: {df.columns.tolist()}")

    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['timestamp'] = df['timestamp'].dt.floor('S').dt.strftime('%Y-%m-%d %H:%M:%S')
    else:
        print("Coluna 'timestamp' não encontrada no DataFrame")

    df = df.replace([float('inf'), float('-inf')], 0)
    df = df.fillna(0)

    values = [df.columns.values.tolist()] + df.values.tolist()

    if values and len(values) > 1:
        sheet.update(values)
    else:
        print("Nada para atualizar na planilha.")


def main():
    midias = get_user_media()
    save_raw_data_to_sheets(midias)
    print(f"{len(midias)} posts salvos na aba 'raw' da planilha.")

if __name__ == "__main__":
    main()  
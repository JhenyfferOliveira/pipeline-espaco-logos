import requests, gspread, os, json
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
INSTAGRAM_USER_ID = os.environ.get("INSTAGRAM_USER_ID")
GOOGLE_CREDENTIALS_JSON = os.getenv("GOOGLE_CREDENTIALS_JSON")
SPREADSHEET_NAME = os.getenv("ong_info_raw")

print("ACCESS_TOKEN:", ACCESS_TOKEN)
print("INSTAGRAM_USER_ID:", INSTAGRAM_USER_ID)

def get_user_media_with_insights():
    url = f"https://graph.facebook.com/v19.0/{INSTAGRAM_USER_ID}/media"
    params = {
        'fields': 'id,caption,media_type,timestamp,permalink,like_count,comments_count',
        'access_token': ACCESS_TOKEN,
        'limit': 100
    }
    
    all_media = []
    while url:
        r = requests.get(url, params=params if not all_media else None)
        data = r.json()
        all_media.extend(data.get('data', []))
        url = data.get('paging', {}).get('next')
        params = None

    # Requisição batch para salvamentos e compartilhamentos
    media_ids = [m['id'] for m in all_media]
    insights = batch_fetch_insights(media_ids)
    
    for media in all_media:
        media_id = media['id']
        media_insights = insights.get(media_id, {"saved": 0, "shares": 0})
        media['saved'] = media_insights.get('saved', 0)
        media['shares'] = media_insights.get('shares', 0)
    
    return all_media

def batch_fetch_insights(media_ids):
    url = "https://graph.facebook.com/v19.0/"
    results = {}
    
    for i in range(0, len(media_ids), 50):
        batch = []
        batch_ids = media_ids[i:i+50]
        for media_id in batch_ids:
            batch.append({
                "method": "GET",
                "relative_url": f"{media_id}/insights?metric=saved,shares"
            })

        r = requests.post(url, params={'access_token': ACCESS_TOKEN}, json={"batch": batch})
        responses = r.json()

        for media_id, resp in zip(batch_ids, responses):
            try:
                data_json = json.loads(resp.get("body", "{}"))
                metrics = {m['name']: m['values'][0]['value'] for m in data_json.get('data', [])}
                results[media_id] = {
                    "saved": metrics.get("saved", 0),
                    "shares": metrics.get("shares", 0)
                }
            except Exception:
                results[media_id] = {"saved": 0, "shares": 0}

    return results

def save_raw_data_to_sheets(data):
    print(f"Quantidade de itens recebidos: {len(data)}")
    if len(data) > 0:
        print(f"Chaves do primeiro item: {data[0].keys()}")
    else:
        print("Nenhum dado recebido!")

    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials_dict = json.loads(GOOGLE_CREDENTIALS_JSON)
    creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)
    client = gspread.authorize(creds)
    spreadsheet = client.open(SPREADSHEET_NAME)

    try:
        sheet = spreadsheet.worksheet('raw')
        sheet.clear()
    except gspread.WorksheetNotFound:
        sheet = spreadsheet.add_worksheet(title='raw', rows='1000', cols='20')

    filtered_data = [item for item in data if 'timestamp' in item]
    print(f"Quantidade de itens com 'timestamp': {len(filtered_data)}")

    df = pd.DataFrame(filtered_data)
    print(f"Colunas do DataFrame: {df.columns.tolist()}")

    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['timestamp'] = df['timestamp'].dt.floor('S').dt.strftime('%Y-%m-%d %H:%M:%S')
    else:
        print("Coluna 'timestamp' não encontrada no DataFrame")

    df = df.replace([float('inf'), float('-inf')], 0).fillna(0)

    values = [df.columns.values.tolist()] + df.values.tolist()

    if values and len(values) > 1:
        sheet.update(values)
    else:
        print("Nada para atualizar na planilha.")

def main():
    media_with_insights = get_user_media_with_insights()
    save_raw_data_to_sheets(media_with_insights)
    print(f"{len(media_with_insights)} posts salvos na aba 'raw' da planilha.")

if __name__ == "__main__":
    main()
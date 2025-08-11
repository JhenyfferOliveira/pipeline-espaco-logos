# Coleta e Envio de Dados da Meta para o Google Sheets e Looker

Projeto desenvolvido para a ONG **Espaço Logos de Cidadania Consciente**, uma organização que promove projetos educativos, culturais e esportivos para crianças e jovens.  
Este repositório contém um ETL que coleta métricas do Instagram da ONG via **Instagram Graph API (Meta)**, salva os dados brutos no **Google Sheets** e alimenta dashboards no **Looker**, tudo automatizado com **GitHub Actions**.

---

## Sobre o Espaço Logos

O Espaço Logos de Cidadania Consciente atua na região da Tijuca (Rio de Janeiro) oferecendo oficinas de educação, cultura e esporte para crianças e jovens em situação de vulnerabilidade, com o objetivo de promover cidadania, cultura e protagonismo juvenil. [Clique aqui](https://espacologos.org.br/) para mais informações.

---

## Funcionamento do Projeto

1. **Coleta de Dados**  
   - Usa a **Instagram Graph API** para buscar todas as mídias do perfil da ONG.  
   - Campos coletados (exemplo): `id`, `caption`, `media_type`, `timestamp`, `permalink`, `like_count`, `comments_count`.

2. **Batch de Insights**  
   - Em lotes (até 50 IDs por requisição) busca `saved` e `shares` via endpoint `/insights?metric=saved,shares` para reduzir número de requisições e tempo.

3. **Armazenamento Raw**  
   - Insere os dados brutos (raw) em uma aba chamada `raw` no Google Sheets (via API).

4. **Automação**  
   - GitHub Actions executa o script por agendamento (cron).

5. **Visualização**  
   - Dados no Google Sheets são usados como fonte para dashboards no Looker.

---

## Dashoard 

---

## Ferramentas Utilizadas

| Python | Google Sheets | Looker | GitHub Actions |
| :----: | :-----------: | :----: | :------------: |
| <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/python/python-original.svg" width="100"> | <img src="https://upload.wikimedia.org/wikipedia/commons/3/30/Google_Sheets_logo_%282014-2020%29.svg" width="50"> | <img src="https://www.svgrepo.com/show/354012/looker-icon.svg" width="80"> | <img src="https://icon.icepanel.io/Technology/svg/GitHub-Actions.svg" width="80"> |

import streamlit as st
import pandas as pd
import requests
import zipfile

def trouver_titre(doi):
    print(doi)
    url = f'https://api.openalex.org/works/doi:{doi}'
    resp = requests.get(url)
    if resp.status_code == 200:
        resp_json = resp.json()
        titre = resp_json['title']
        return titre
    else:
        return "Erreur"

df_liste=[]

uploaded_files = st.file_uploader(
    "Upload files", accept_multiple_files="directory", type=["xlsx","csv"]
)
for uploaded_file in uploaded_files:
    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file)
        st.write(df)

        if st.button("Moissonnage OpenAlex"):
            df['Titre'] = df['DOI'].apply(lambda x: trouver_titre(x))
            st.write(df)

    df_liste.append(df)

    @st.cache_data
    def convert_df(df):
        return df.to_csv(index=False).encode('utf-8')

    csv = convert_df(df)

with zipfile.ZipFile('fichiers_etablissements.zip', 'w', zipfile.ZIP_DEFLATED) as csv_zip:
    for file,f in zip(df_liste,uploaded_files):
        filename=f.name
        file.to_csv(f"{filename}",index=False)
        csv_zip.writestr(f"{filename}")

with open("fichiers_etablissements.zip", "rb") as z:
    btn = st.download_button(
            label = "Download zip",
            data = z,
            file_name = "fichiers_etablissements.zip",
            mime = "application/zip"
          )
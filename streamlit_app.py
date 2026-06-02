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

uploaded_files = st.file_uploader(
    "Upload images", accept_multiple_files="directory", type=["jpg", "png"]
)
for uploaded_file in uploaded_files:
    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file)
        st.write(uploaded_file)

        if st.button("Moissonnage OpenAlex"):
            df['Titre'] = df['DOI'].apply(lambda x: trouver_titre(x))
            st.write(df)

    @st.cache_data
    def convert_df(df):
        return df.to_csv(index=False).encode('utf-8')

    csv = convert_df(df)

    with ZipFile('fichiers_etablissements.zip', 'w') as csv_zip:
        for file in directory:
            df.to_csv(f'sample_{i}.csv') #this will convert the dataframe to a .csv
            zf.write(f'sample_{i}.csv') #this will put the .csv in the zipfile
            os.remove(f'sample_{i}.csv') #this will delete the .csv created 

st.download_button(
    label="Download zip",
    data=buf.getvalue(),
    file_name="fichiers_établissements.zip",
    mime="application/zip",
)
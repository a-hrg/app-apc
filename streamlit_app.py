import streamlit as st

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

uploaded_file = st.file_uploader("Choose a file")
if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    st.write(df)


    if st.button("API"):
        df['Titre'] = df['DOI'].apply(lambda x: trouver_titre(x))
        st.write(df)

    @st.cache_data
    def convert_df(df):
        return df.to_csv(index=False).encode('utf-8')

    csv = convert_df(df)

    st.download_button(
        "Press to Download",
        csv,
        "file.csv",
        "text/csv",
        key='download-csv'
    )
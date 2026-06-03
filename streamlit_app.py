import streamlit as st
import json
from pathlib import Path
import pandas as pd
import requests
import zipfile

#####----- paramètres + fonctions

API_KEY = "NeiyFtd6q8vUxkDmPXjK8g"
headers = {'api_key': f'{API_KEY}'}

df_liste=[]

def doi_api(doi):
    if not doi or type(doi)==float: return "False"

    doi = doi.strip()
    url = f'https://api.openalex.org/works/https://doi.org/{doi}'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        responses_json = json.loads(response.content.decode('utf-8'))
        return responses_json
    else:
        return "False"

def titre_doi(responses_json):
    if responses_json=="False": return "False"
    title = responses_json.get('title')
    return title

def licence_doi(responses_json):
    if responses_json == "False": return "False"
    primary_location = responses_json.get('primary_location')
    if not primary_location:
        return "False"
    else:
        license = primary_location.get('license')
        return license

def annee_doi(responses_json):
    if responses_json == "False": return "False"
    annee = responses_json.get('publication_year')
    return annee

def revue_doi(responses_json):
    if responses_json == "False": return "False"
    primary_location = responses_json.get('primary_location')
    if not primary_location:
        return "False"
    else:
        source = primary_location.get('source')
        if not source:
            return "False"
        else:
            display_name = source.get('display_name')
            return display_name
        
def issn_doi(responses_json):
    if responses_json == "False": return "False"
    primary_location = responses_json.get('primary_location')
    if not primary_location:
        return "False"
    else:
        source = primary_location.get('source')
        if not source:
            return "False"
        else:
            issn_l = source.get('issn_l')
            return issn_l

def editeur_doi(responses_json):
    if responses_json == "False": return "False"
    primary_location = responses_json.get('primary_location')
    if not primary_location:
        return "False"
    else:
        source = primary_location.get('source')
        if not source:
            return "False"
        else:
            host_organization_name = source.get('host_organization_name')
            return host_organization_name

def oa_doi(responses_json):
    if responses_json == "False": return "False"
    open_access = responses_json.get('open_access')
    if not open_access:
        return "False"
    else:
        oa_status = open_access.get('oa_status')
        if not oa_status:
            return "False"
        else:
            return oa_status

def auteur_doi(responses_json):
    liste=[]
    if responses_json == "False": return "False"

    authorships=responses_json.get('authorships')
    if not authorships: return "False"
    
    for a in authorships:
        if a.get('is_corresponding')==True:
            auteur = a.get('author')
            auteur_nom = auteur.get('display_name')
            liste.append(auteur_nom)

    if not liste: return "False"

    auteurs = ', '.join(liste)
    return auteurs

#####----- main

st.title('Enquête APC - Enrichissement')

uploaded_files = st.file_uploader(
    "Sélectionner le dossier contenant les fichiers à traiter :", accept_multiple_files="directory", type=["xlsx","csv"]
)

if uploaded_files:
    if st.button("Moissonnage OpenAlex"):
        for file in uploaded_files:
            if file is not None:
                with st.spinner("En cours...", show_time=True):
                    df = pd.read_excel(file)
                    df['rep_api'] = df['DOI'].apply(lambda x: doi_api(x))

                    df['Titre'] = df['rep_api'].apply(lambda x: titre_doi(x))
                    df['Auteur de correspondance'] = df['rep_api'].apply(lambda x: auteur_doi(x))
                    df['Revue'] = df['rep_api'].apply(lambda x: revue_doi(x))
                    df['ISSN_L'] = df['rep_api'].apply(lambda x: issn_doi(x))
                    df['Editeur'] = df['rep_api'].apply(lambda x: editeur_doi(x))
                    df['Année de publication'] = df['rep_api'].apply(lambda x: annee_doi(x))
                    df['Licence'] = df['rep_api'].apply(lambda x: licence_doi(x))
                    df['Statut_OA'] = df['rep_api'].apply(lambda x: oa_doi(x))

                    df=df.drop(columns=['rep_api'])
                    st.write(df)
                    df_liste.append(df)

        with zipfile.ZipFile('enquete_etablissements_modifies.zip', 'w') as zf:
            for df,file in zip(df_liste,uploaded_files):
                filename=file.name
                filename=Path(filename).stem
                df.to_csv(f'{filename}_modifié.csv') #this will convert the dataframe to a .csv
                zf.write(f'{filename}_modifié.csv') #this will put the .csv in the zipfile

        with open('enquete_etablissements_modifies.zip', 'rb') as f:
            st.download_button('Télécharger le zip', f, file_name='enquete_etablissements_modifies.zip')
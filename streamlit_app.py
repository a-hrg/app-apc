import streamlit as st
import json
from pathlib import Path
import pandas as pd
import requests
import zipfile

#####----- paramètres + fonctions

API_KEY = st.secrets['API_KEY']
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

def statut_revue(issn):
    if not issn or issn=='False': return "False"

    url = f'https://api.openalex.org/sources/issn_l:{issn}'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        responses_json = json.loads(response.content.decode('utf-8'))
        is_oa=responses_json.get('is_oa')
        if is_oa==False: return "Hybride"
        else: return "Full OA"

def doublon_compil(doi):
    doi_compilation=compilation['DOI'].to_list()
    if doi in doi_compilation:
        return "True"
    else:
        return "False"

#####----- main

st.title('Enquête APC - Enrichissement')

uploaded_files = st.file_uploader(
    "Sélectionner le dossier contenant les fichiers à traiter :", accept_multiple_files="directory", type=["xlsx","csv"]
)

compilation_file = st.file_uploader(
    "Charger la compilation APC", accept_multiple_files=True, type=["xlsx","csv"]
)

for file in compilation_file:
    compilation = pd.read_excel(file)

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
                    df['Issn_l'] = df['rep_api'].apply(lambda x: issn_doi(x))
                    df['Type de revue'] = df['Issn_l'].apply(lambda x: statut_revue(x))
                    df['Editeur'] = df['rep_api'].apply(lambda x: editeur_doi(x))
                    compilation_editeur=compilation[['TypeEditeur','Issn_l']]
                    compilation_editeur=compilation_editeur.drop_duplicates(subset=['Issn_l'])
                    df = df.merge(compilation_editeur,on="Issn_l",how="left")
                    df['Année de publication'] = df['rep_api'].apply(lambda x: annee_doi(x))
                    df['Licence'] = df['rep_api'].apply(lambda x: licence_doi(x))
                    df['Statut_OA'] = df['rep_api'].apply(lambda x: oa_doi(x))
                    df['Compilation_Doublon'] = df['DOI'].apply(lambda x: doublon_compil(x))
                    df=df.drop(columns=['rep_api'])
                    st.write(df)
                    df_liste.append(df)

        with zipfile.ZipFile('enquete_etablissements_modifies.zip', 'w') as zf:
            for df,file in zip(df_liste,uploaded_files):
                filename=file.name
                filename=Path(filename).stem
                df.to_excel(f'{filename}_modifié.xlsx', index=False)
                zf.write(f'{filename}_modifié.xlsx')

    with open('enquete_etablissements_modifies.zip', 'rb') as f:
        st.download_button('Télécharger le zip', f, file_name='enquete_etablissements_modifies.zip')
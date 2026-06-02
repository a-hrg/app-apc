from flask import Flask, Response, render_template
import pandas as pd
import os
import requests

app = Flask(__name__)

@app.route('/')
def generate_csv():
    user = os.getlogin()
    df = pd.read_excel(rf'C:\Users\{user}\Downloads\DOI_sans_titres.xlsx')
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

    #df['Titre'] = df['DOI'].apply(lambda x: trouver_titre(x))

    html_df = df.to_html(classes='data', header="true")

    return render_template('home.html', tables=html_df)

@app.route('/download')
def download():
    return send_file(df)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

# A faire :
# upload de fichier -> enrichissement openalex -> export du fichier
# https://blog.miguelgrinberg.com/post/handling-file-uploads-with-flask

# Déployer site sur même architecture mais pour les accords A&T avec dashboard ?
from flask import Flask, Response, render_template
import pandas as pd

app = Flask(__name__)

@app.route('/')
def generate_csv():
    df = pd.read_excel(rf'C:\Users\FélixHeranger\Downloads\DOI_pour_licence.xlsx')
    html_df = df.to_html(classes='data', header="true")
    return render_template('home.html', tables=html_df)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)

# A faire :
# upload de fichier -> enrichissement openalex -> export du fichier
# https://blog.miguelgrinberg.com/post/handling-file-uploads-with-flask

# Déployer site sur même architecture mais pour les accords A&T avec dashboard ?
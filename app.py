from flask import Flask, render_template
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from bs4 import BeautifulSoup 
import requests
import re

#don't change this
matplotlib.use('Agg')
app = Flask(__name__) #do not change this

#insert the scrapping here
response = requests.get('https://www.imdb.com/search/title/?release_date=2019-01-01,2019-12-31')
page_html = BeautifulSoup(response.text, 'html.parser')
# Select all 50 film in a container
mv_containers = page_html.find_all('div', class_ = 'lister-item mode-advanced')
# Select all 50 film in a container
nama_film = []
imdb_ratings = []
user_votes = []
metascores = []
for container in mv_containers:
    #finding Name Of film 
    name = container.h3.a.text
    nama_film.append(name)
    #print(name)
    
    #finding IMDB rating
    imdb = container.strong.text
    imdb_ratings.append(imdb)
    #print (imdb)  
    
    #finding user votes
    vote = container.find('span', attrs = {'name':'nv'})['data-value']
    user_votes.append(int(vote))
    
    #finding metascore
    if container.find('div', class_ = 'ratings-metascore') is not None:
        m_score = container.find('span', class_ = 'metascore').text
        metascores.append(int(m_score))
    else:
        #if a movie did not have metascore then we append 0
        metascores.append(int(0))
        

#change into dataframe
data =pd.DataFrame({"Judul Film": nama_film, "IMDB Rating": imdb_ratings, "Votes": user_votes, "Metascore": metascores})

#insert data wrangling here
data['IMDB Rating'] = data['IMDB Rating'].astype('float64') 
data['Votes'] = data['Votes'].astype('float64')
data['Metascore'] = data['Metascore'].astype('float64')
data.set_index("Judul Film", inplace=True)
#end of data wranggling 

@app.route("/")
def index(): 
	
	card_data = f'Judul Film Paling Populer berdasarkan Vote User {data["Votes"].mean().round(2)}'

	# generate plot
	ax = data.sort_values("Votes", ascending=False).head(7).plot.bar()

	
	# Rendering plot
	# Do not change this
	figfile = BytesIO()
	plt.savefig(figfile, format='png', transparent=True)
	figfile.seek(0)
	figdata_png = base64.b64encode(figfile.getvalue())
	plot_result = str(figdata_png)[2:-1]


	# render to html
	return render_template('index.html',
		card_data = card_data, 
		plot_result=plot_result
		)


if __name__ == "__main__": 
    app.run(debug=True)

from flask import Flask,render_template,request,jsonify,redirect
import requests
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64
import pandas as pd
import urllib.parse

app=Flask(__name__)

movie_names=requests.get('http://127.0.0.1:8000/movie_list').json()
show_names=requests.get('http://127.0.0.1:8000/shows_list').json()
years = requests.get('http://127.0.0.1:8000/year_list').json()
ratings = requests.get('http://127.0.0.1:8000/rating_list').json()

movies = [movie[0] for movie in movie_names]
shows = [show[0] for show in show_names]
year = [str(year[0]) for year in years]  
m_ratings = [rating[0] for rating in ratings]

categories = {
    "Movie": movies,
    "TV Shows": shows,
    "Year": year,
    "Maturity Rating": m_ratings
}



@app.route('/')
def index():
    url1 = 'http://127.0.0.1:8000/stats'
    url2 = 'http://127.0.0.1:8000/bar_plot'
    url3 = 'http://127.0.0.1:8000/doughnut_plot'
    
    response1 = requests.get(url1)
    response2 = requests.get(url2)
    response3 = requests.get(url3)
    
    if response1.status_code == 200 and response2.status_code == 200 and response3.status_code == 200:
        stats = response1.json()
        bar_data = response2.json()
        doughnut_data = response3.json()
    
        year_type_data = pd.DataFrame(bar_data)
        
        years_to_plot=[str(year) for year in range(1990,2024)]
        year_type_datas=year_type_data[year_type_data['release_year'].astype(str).isin(years_to_plot)][["release_year","type","count"]]
        
        year_type_counts=year_type_datas.groupby(["release_year","type"]).sum().unstack(fill_value=0)
        
        fig,ax=plt.subplots(figsize=(15,10))
        year_type_counts.plot(kind="bar",ax=ax)

        ax.set_xlabel("Year of Release",fontsize=30)
        ax.set_ylabel("Count",fontsize=20)
        ax.set_title("Distribution of Movies & TV Shows from 1990 to 2022",fontsize=35)
        plt.xticks(rotation=45)
        plt.legend(title="Type",fontsize=20,title_fontsize='13')

        bar_img = io.BytesIO()
        plt.savefig(bar_img, format='png')
        bar_img.seek(0)
        plt.close()
        bar_plot_url = base64.b64encode(bar_img.getvalue()).decode()

        labels = [d["Maturity_Rating"] for d in doughnut_data]
        sizes = [d["rating_counts"] for d in doughnut_data]
        colors = ['#FF6B6B', '#FFD93D', '#6BCB77', '#4D96FF', '#9B59B6', '#F39C12', '#34495E', '#7DCEA0', '#E74C3C']
        fig, ax = plt.subplots()
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors, startangle=20, wedgeprops=dict(width=0.3))
        centre_circle = plt.Circle((0,0),0.70,fc='white')
        fig.gca().add_artist(centre_circle)
        ax.axis('equal') 
        doughnut_img = io.BytesIO()
        plt.title('Distribution of Maturity Ratings')
        plt.savefig(doughnut_img, format='png')
        doughnut_img.seek(0)
        plt.close()
        doughnut_plot_url = base64.b64encode(doughnut_img.getvalue()).decode()

        return render_template('dashboard.html', stats=stats, bar_plot=bar_plot_url, doughnut_plot=doughnut_plot_url, data='')
    else:
        return render_template('dashboard.html', stats='', bar_plot='', doughnut_plot='',data = '')


@app.route('/search', methods=['GET', 'POST'])
def searching():
    if request.method == 'POST':
        option = request.form.get('category')
        value1 = request.form.get('query')
    else:
        option = request.args.get('category')
        value1 = request.args.get('query')

    ITEMS_PER_PAGE = 10 
    page = request.args.get('page', 1, type=int)
    error=""
    
    endpoints = {
        "Movie": "http://127.0.0.1:8000/search_movie/?movie=",
        "TV Shows": "http://127.0.0.1:8000/search_movie/?movie=",
        "Year": "http://127.0.0.1:8000/year_result/",
        "Maturity Rating": "http://127.0.0.1:8000/rating_result/"
    }


    if option in endpoints and value1:

        if option != "Maturity Rating":
            value = urllib.parse.quote(value1).replace("/","%2F")
        else:
            value = value1

        response = requests.get(f"{endpoints[option]}{value}")

        if response.status_code == 200:
            try:
                data = response.json()
            except ValueError:
                data = []
                error = "Invalid response from API"
        else:
            data = []
            error = "Failed to fetch data from API"

        if not data:
            result = []
            error ="No Result Found"
            current_data = []
            total_pages = 1
            pagination_range_start = 1
            pagination_range_end = 1
        else:
            result = data
            start = (page - 1) * ITEMS_PER_PAGE
            end = start + ITEMS_PER_PAGE
            current_data = result[start:end]
            total_pages = (len(result) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE

            pagination_range_start = max(1,page -1)
            pagination_range_end = min(total_pages , page+3)

        return render_template('search.html', data=error, datas=current_data, page=page, total_pages=total_pages, option=option, query=value1, pagination_range_start=pagination_range_start, pagination_range_end=pagination_range_end)
    else:
        return redirect('/')

@app.route('/get_suggestions', methods=['POST'])
def get_suggestions():
    category = request.form.get('category')
    query = request.form.get('query', '').lower()
    
    suggestions = []
    if category in categories:
        suggestions = [item for item in categories[category] if query in item.lower()]
    elif category == 'select_category':
        suggestions= ["Please Select Category"]

    return jsonify({"suggestions": suggestions})

if __name__=='__main__':
    app.run(debug=True)
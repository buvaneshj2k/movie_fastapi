from fastapi import FastAPI, HTTPException, Query
import mysql.connector
from mysql.connector import Error

app = FastAPI()

def connect():
    try:
        return mysql.connector.connect(
            host='3.7.198.191',
            user='bu-trausr',
            password='r9*rwr$!usFw0MCPj#fJ',
            database='bu-training',
            port=8993,
            auth_plugin='mysql_native_password'
        )
    except Error as e:
        raise HTTPException(status_code=500, detail="Database connection failed")

@app.get("/stats")
async def get_stats():
    try:
        con = connect()
        cur = con.cursor(dictionary=True)
        query = """
            SELECT 
                (SELECT COUNT(*) FROM python_amazon_movie_ott) AS total_movies_shows,
                (SELECT COUNT(*) FROM python_amazon_movie_details WHERE type = 'Movie') AS total_movies,
                (SELECT COUNT(*) FROM python_amazon_movie_details WHERE type = 'TV Show') AS total_shows
        """
        cur.execute(query)
        stats = cur.fetchone()
        cur.close()
        con.close()
        return stats
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {e}")

@app.get('/search_movie/')
async def movie_search(movie: str = Query(...)):
    try:
        con = connect()
        cur = con.cursor()
        query = """
            SELECT mo.id, mo.movie_name, md.type, md.duration, md.release_year, md.maturity_rating, md.description, mo.ott
            FROM python_amazon_movie_ott mo
            JOIN python_amazon_movie_details md ON mo.details_id = md.id
            WHERE mo.movie_name = %s
        """
        cur.execute(query, (movie,))
        result = cur.fetchall()
        cur.close()
        con.close()
        return result
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {e}")

@app.get('/movie_list')
async def movie_list():
    try:
        con = connect()
        cur = con.cursor()
        query = """
            SELECT mo.movie_name
            FROM python_amazon_movie_ott mo
            JOIN python_amazon_movie_details md ON mo.details_id = md.id
            WHERE md.type = 'Movie'
        """
        cur.execute(query)
        values = cur.fetchall()
        cur.close()
        con.close()
        return values
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {e}")

@app.get('/shows_list')
async def show_list():
    try:
        con = connect()
        cur = con.cursor()
        query = """
            SELECT mo.movie_name
            FROM python_amazon_movie_ott mo
            JOIN python_amazon_movie_details md ON mo.details_id = md.id
            WHERE md.type = 'TV Show'
        """
        cur.execute(query)
        values = cur.fetchall()
        cur.close()
        con.close()
        return values
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {e}")

@app.get('/year_list')
async def year_list():
    try:
        con = connect()
        cur = con.cursor()
        query = "SELECT DISTINCT(release_year) FROM python_amazon_movie_details"
        cur.execute(query)
        values = cur.fetchall()
        cur.close()
        con.close()
        return values
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {e}")

@app.get('/rating_list')
async def rating_list():
    try:
        con = connect()
        cur = con.cursor()
        query = "SELECT DISTINCT(maturity_rating) FROM python_amazon_movie_details"
        cur.execute(query)
        values = cur.fetchall()
        cur.close()
        con.close()
        return values
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {e}")

@app.get('/doughnut_plot')
async def plot_pie():
    try:
        con = connect()
        cur = con.cursor(dictionary=True)
        query = """
            SELECT md.maturity_rating as Maturity_Rating, COUNT(*) AS rating_counts
            FROM python_amazon_movie_ott mo
            JOIN python_amazon_movie_details md ON mo.details_id = md.id
            GROUP BY md.maturity_rating
        """
        cur.execute(query)
        values = cur.fetchall()
        cur.close()
        con.close()
        return values
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {e}")

@app.get('/bar_plot')
async def plot_bar():
    try:
        con = connect()
        cur = con.cursor(dictionary=True)
        query = """
            SELECT md.release_year, md.type, COUNT(*) AS count
            FROM python_amazon_movie_ott mo
            JOIN python_amazon_movie_details md ON mo.details_id = md.id
            WHERE md.release_year BETWEEN 1990 AND 2022
            GROUP BY md.release_year, md.type
            ORDER BY md.release_year
        """
        cur.execute(query)
        values = cur.fetchall()
        cur.close()
        con.close()
        return values
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {e}")

@app.get('/year_result/{year}')
async def search_year(year: int):
    try:
        con = connect()
        cur = con.cursor()
        query = """
            SELECT mo.id, mo.movie_name, md.type, md.duration, md.release_year, md.maturity_rating, md.description, mo.ott
            FROM python_amazon_movie_ott mo
            JOIN python_amazon_movie_details md ON mo.details_id = md.id
            WHERE md.release_year = %s
        """
        cur.execute(query, (year,))
        values = cur.fetchall()
        cur.close()
        con.close()
        return values
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {e}")

@app.get('/rating_result/{rate}')
async def search_rating(rate: str):
    try:
        con = connect()
        cur = con.cursor()
        query = """
            SELECT mo.id, mo.movie_name, md.type, md.duration, md.release_year, md.maturity_rating, md.description, mo.ott
            FROM python_amazon_movie_ott mo
            JOIN python_amazon_movie_details md ON mo.details_id = md.id
            WHERE md.maturity_rating = %s
        """
        cur.execute(query, (rate,))
        values = cur.fetchall()
        cur.close()
        con.close()
        return values
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {e}")

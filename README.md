# Project 1

This application is a book review and ratings site with access upto 5000 books and it displays data using Goodread's api. It has been created using Flask, PostgresSql, html-css, and JavaScript.

File details-

application.py: contains the Flask app with all the information of it's routes and interactions with the postgres DB.
  ./books/isbn: this url will take you to the book with the given isbn.
  ./api/isbn: this url displays the results consisting of the book’s title, author, publication date, ISBN number, review count, and average score in JSON schema.  
extra_functions.py: python script to verify password constraints.
import.py: python script to import data from "books.csv" and insert into the DB.
templates: files containing html5 layout for the app.
templates/includes: html files containing helpers for the wtforms.
static: contains CSS/SCSS and JavaScript files used in the app.
requirements.txt: contains list of all python packages used by the app.

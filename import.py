import os
import requests
import csv
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from random import randint

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():
    file = open("books.csv")
    csvReader = csv.reader(file)
    count = 0;
    for isbn, title, author, year in csvReader:
        if count == 0:
            count+=1
        else:
            res = db.execute("SELECT * FROM authors").fetchall()
            id_list =  [x['id'] for x in res]
            # chech is author exists
            if author not in [x['name'] for x in res]:
                # generate random unique id
                while True:
                    id = randint(1000, 9999)
                    if id not in id_list:
                        break

                db.execute("INSERT INTO authors(id, name) VALUES(:id, :name)", {"id": id, "name": str(author)})
            db.commit()
            print(isbn)

            db.execute("INSERT INTO books(isbn, title, publication_year, author_id) VALUES(:isbn, :title, :year, :id)", {"isbn": isbn, "title": title, "year": year, "id": db.execute("SELECT * FROM authors WHERE name = :author", {"author": author}).fetchone()['id']})
    db.commit()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3

import psycopg2
import decimal


# the database within
DBNAME = "news"


def toparticles():
    # Connect to database
    db = psycopg2.connect(database=DBNAME)

    # Connect to database
    c = db.cursor()

    # Putting PostgreSQL code into a variable
    query = """ create view toparticles as
                    select articles.title, count(log.path) as num
                    from articles, log
                    where '/article/' || articles.slug = log.path
                    group by title
                    order by num desc
                    limit 3;

                select * from toparticles;"""

    # Queries through databse
    c.execute(query)

    # Fetches all results from query
    posts = c.fetchall()

    # Closes database session
    db.close()
    return posts


def topauthors():
    db = psycopg2.connect(dbname=DBNAME)
    c = db.cursor()
    query2 = """ create view topauthors as
                    select authors.name, count(log.path) as num
                    from articles, log, authors
                    where '/article/' || articles.slug = log.path
                            and articles.author = authors.id
                            and authors.name != 'Anonymous Contributor'
                    group by name
                    order by num desc
                    limit 3;


                select * from topauthors;"""
    c.execute(query2)
    posts2 = c.fetchall()
    db.close()
    return posts2


def errorsperc():
    db = psycopg2.connect(dbname=DBNAME)
    c = db.cursor()
    query3 = """create view Error as
                    select substring(CAST (time AS text) from 1 for 10)
                            as date, cast(count(status) as float) as errors
                    from log
                    where status = '404 NOT FOUND'
                    group by date
                    order by date desc;

                create view Total as
                    select substring(CAST (time AS text) from 1 for 10)
                            as date2, cast(count(status) as float) as totals
                    from log
                    group by date2
                    order by date2 desc;

                select a.date, a.errors/b.totals*100
                from Error a, total b
                where a.errors/b.totals*100 > 2 and a.date = b.date2
                order by a.date desc;"""
    c.execute(query3)
    posts3 = c.fetchall()
    db.close()
    return posts3


# headline before ranking
print('Top 3 Most Popular Articles')
num = 1
# loops through each row in the query
for row in toparticles():

    # row[0] and row[1] being the first and second column, respectively
    stat = (str(num) + '.) ' + str(row[0]) + ": " +
            str(('{:,}'.format(row[1]))) + ' views')

    # Increments num for its position in the ranking
    num += 1
    print(stat)

print('\nTop 3 Most Popular Authors')
num2 = 1
for row in topauthors():
    stat = (str(num2) + '.) ' + str(row[0]) + ": " +
            str(('{:,}'.format(row[1]))) + ' views')
    print(stat)
    num2 += 1

print('\nDays when errors exceeded 1%:')
for row in errorsperc():

    # Imported decimal to round to the nearest hundredth
    # % and error are separate strings, caused my laptop to crash when combined
    stat = (str(row[0]) + ": " + str(round(decimal.Decimal(row[1]), 2)) +
            '%' + ' errors')
    print(stat)

#### Author: Emerson Pourghaed | Version: 1.0.2 | Last Modified: 8/9/2018

# Python Project: Logs Analysis
Python code running postgreSQL to query news database, returning the top 3 ranking of the most viewed articles and authors, and day in which error rates exceeded 2%.

## Getting Started
Download newsdata.py from this folder's repository, along with the prerequisites.

### Prerequisites
Project functions with the following:
* newsdata.sql and VM configuration - Downloaded from Udacity
* Python (3.61) - used to run Python's code
* Vagrant (1.9.5) - Used for displaying and querying database. Once installed from vagrantup's website, use vagrant --version in git to check if vagrant is running
* Oracle's VM VirtualBox Manager (5.1.22) - for running vagrant
* psycopg2 (2.7.1) - For opening and executing the database within Python code. In order to use this import, pip install psycopg2 through git, within the virtual environment

First, the VM configuration was placed in the (C:) drive. From there, open up git and locate the folder where Vagrantfile is located. From here, use the command 'vagrant up'  and 'vagrant ssh' to be able to view and query the database.

In order to view the tables within the database, use the command '\dt'. A table should show up with the 3 tables that are available: articles, authors and log. In order to view the columns within the table, use the command '\d [insert table name here]'.

### Installing
Download, or CTRL+C, the code found in /Logs_Analysis/newsdata.py, which inlcude the python files listed below.

### Running the tests
1. Through Git Bash, navigate to the Vagrantfile
2. Vagrant Up to get VM VirtualBox running
3. Vagrant SSH to log in
4. use the command 'cd /vagrant' to move out of home/vagrant to the vagrant folder that holds the files newsdata.py and newsdata.sql
5. to run, type 'python newsdata.py' and the results from the queries will process, note: some of the queries will take up to 10 seconds
6. If queries are modified and are taking a while to process, CTRL+C wont leave the process CTRL+Z will end the process, but wont guarantee the process will run properly. What would be suggested is to restart Git Bash and following the process sans the command vagrant up.

#### Breakdown on how to modify newsdata.py:

There's 3 functions that query through the database: toparticles, topauthors and errorperc. Each one following the same format of connecting to the database through psycopg2, putting postgreSQL code into a query variable, executing, fetching all the findings, closing the database and returning the information.
```python
def top articles():
    db = psycopg2.connect(dbname=DBNAME)
    c = db.cursor()
    query = """ /* PostgreSQL query syntax goes here */"""
    c.execute(query)
    posts2 = c.fetchall()
    db.close()
    return posts
```

The 3 functions are called through their respective loops that goes through each row, row[0]  and row[1] being the columns for the descriptive string and integer. Each function has a printed headline right before, and the printed stat that concatenates each row after. The first two queries have an incrementing num for numerically ranking the articles and authors.
```python
print('Top 3 Most Popular Articles')
num = 1
for row in toparticles():
    stat = str(num) + '.) ' + str(row[0]) + ": " + str(('{:,}'.format(row[1]))) + ' views'
    num += 1
    print(stat)
```
Some formating syntax were added for readability; the first one puts a comma for integers in the thousands and millions, and the second rounds the float into the nearest hundredth.
```python
str(('{:,}'.format(row[1])))

str(round(decimal.Decimal(row[1]), 2))
```

To sample the third query, the goal of the query was to catch the days where the percentage of 404 HTTP status from clicking the articles url were greater than 2%.

### Creating Views for Query

Two views were made for aggregating the errors and totals grouped by their date. The substring is used on the time column to reduce the information gathered to only YEAR-MM-DD, instead of capturing the specific hour and second, which is then given the nickname 'date'. The numbers are then grouped by the day, and the errors view uses a where to specifcally count the strings '404 NOT FOUND', while the totals counts all the status codes including 2XX.

Bellow are the two created views used in the project: Error and Total. Both views have the same function of selecting the time and counting the number of status codes, where the former has a where function that only selects for a status code equal to 404.

```sql
create view Error as
    select substring(CAST (time AS text) from 1 for 10) as date, cast(count(status) as float) as errors
    from log
    where status = '404 NOT FOUND'
    group by date
    order by date desc;
```

```sql
create view Total as
    select substring(CAST (time AS text) from 1 for 10) as date2, cast(count(status) as float) as totals
    from log
    group by date2
    order by date2 desc;
```

The views are then brought together to select for the days and their percentage of the statuses were 404. The views are called with the from function, with Error being give the abbreviation a and total with the abbreviation b. The date, errors and totals have the 'a.' and 'b.' to indicate which view they originated from. In the where function, percentages are cut to only select for the days greater than 2 (for 2%), and the dates are made sure as being the same.

```sql
select a.date, a.errors/b.totals*100
from Error a, total b
where a.errors/b.totals*100 > 2 and a.date = b.date2
order by a.date desc;
```

### Alternative to views: subqueries

An alternative to the same function as above is creating subqueries within the queries, to replace the 2 views from before. The names of the subqueries are after the parenthesis; named a and b.

```sql
select a.date, a.errors/b.totals*100
from (select substring(CAST (time AS text) from 1 for 10) as date, cast(count(status) as float) as errors
        from log
        where status = '404 NOT FOUND'
        group by date
        order by date desc) a
    , (select substring(CAST (time AS text) from 1 for 10) as date2, cast(count(status) as float) as totals
        from log
        group by date2
        order by date2 desc) b
where a.errors/b.totals*100 > 2 and a.date = b.date2
order by a.date desc;
```

### Acknowledgments
Used Instructions for setting up VM VirtualBox and Vagrant from Udacity, along with tutorials on Python and PostgreSQL.

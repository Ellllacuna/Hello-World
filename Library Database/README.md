# Overview

This Library Catalog Program is a Python application designed to manage basic library operations by integrating with a MySQL relational database. It allows patrons and staff to view, check out, and return books, register new customers, and manage overdue fines. 


[Software Demo Video](https://www.youtube.com/watch?v=YMQRX7XTKFM)

# Relational Database

The database used in this project is designed to model a real-world library environment. Its goal is to maintain structured data about books, patrons, and transactions. It features established relationships between different entities to enforece data consistency and real-world logic within the database.

The SQL database includes the following key tables:
- book: Stores information about individual books, including title, isbn, and publisher.
- author: Stores the first and last name of an author.
- customer: Stores patron information such as name, email, and phone number.
- loan: Tracks which customer has borrowed which book as well as the loan's status.
- fine: Records paid and unpaid fines for overdue books.

# Development Environment

- VS code
- MySQL Workbech

- SQL
- Python

- mysql.connector
- datetime

# Useful Websites

- [MySQL connector](https://pypi.org/project/mysql-connector-python/)
- [W3 Schools SQL Tutorial](https://www.w3schools.com/sql/)

# Future Work

- Get rid of repeating code by creating helper functions
- Use try-except blocks to avoid bugs and problems
- Create a way to keep track of multiple copies of books.
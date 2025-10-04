CREATE DATABASE LibraryCatalog;
USE LibraryCatalog;

CREATE TABLE book (
    book_id INT PRIMARY KEY,
    title VARCHAR(225),
    isbn VARCHAR(13),
    publisher VARCHAR(100),
    year_published INT);

CREATE TABLE genre (
	genre_id INT PRIMARY KEY Auto_Increment,
    name VARCHAR(50));
    
CREATE TABLE bookgenre (
	book_id int,
    foreign key (book_id) references book(book_id),
    genre_id int, 
    foreign key (genre_id) references genre(genre_id));
    
CREATE TABLE author (
	author_id INT PRIMARY KEY AUTO_INCREMENT,
    first_name VARCHAR(100),
    last_name VARCHAR(100)
);

ALTER TABLE book
ADD author_id INT;

ALTER TABLE book
ADD CONSTRAINT fk_author_id
FOREIGN KEY (author_id)
REFERENCES author(author_id);
    
INSERT INTO book (title, isbn, publisher, year_published) VALUES
('You Like It Darker', '9781668037713', 'Scribner', 2024);
UPDATE book SET author_id = 1 WHERE book_id = 1;
INSERT INTO author (first_name, last_name) VALUES
('Stephen', 'King');

INSERT INTO genre (name) values
('Mystery'),('Historical Fiction'),('Autobiography'),('Romance'),('Classics'),('Fantasy'),('Crime'),
('Horror'),('Nonfiction'),('Paranormal'),('Religion'),('Science Fiction'),('Self Help'),('Sports'),
('High Fantasy'), ('Western'),('Thriller');

INSERT INTO book (title, isbn, publisher, year_published, author_id) VALUES
('The Book Thief', '9780552773898', 'Black Swan', 2007, 2),
('The Diary of a Young Girl','9780141182759', 'Penguin Modern Classics', 2000, 3),
('The Fault in Our Stars', '9780525478812', 'Dutton Books', 2012, 4),
('1984','9780452284234','Plume',2022,5),
('Six of Crows', '9781627792127','Henry Holt & Company',2015,6),
('The Girl With the Dragon Tattoo', '9780670069019', 'Viking Canada', 2008, 7),
('The Shining','9780450040184','New English Library',1980,1),
('Educated','9780399590504','Random House',2018,8), /* book_id: 9 */
('Twilight', '9780316015844', 'Little, Brown and Company', 2006, 9),
('Under the Banner of Heaven: A Story of Violent Faith','9780330419123','Pan MacMillan',2004,10),
('Dune','9780593099322', 'Ace',2019,11),
('The Life-Changing Magic of Tidying Up: The Japanese Art of Decluttering and Organizing','9781607747307','Ten Speed Press',2014,12),
('Life, and Death, and Giants','9781250375339', "St. Martin's Press", 2025,13),
('The Fellowship of the Ring', '9780618346257', 'Houghton Mifflin Harcourt', 2003,14),
('LoneSome Dove', '9780671683900', 'Pocket Books',1999,15),
('The Silent Patient', '9781250301697', 'Celadon Books', 2019,16);
INSERT INTO author (first_name, last_name) values
('Markus', 'Zusak'),
('Anne', 'Frank'),
('John', 'Green'),
('George', 'Orwell'),
('Leigh','Bardugo'),
('Stieg', 'Larsson'),
('Tara', 'Westover') /* author_id: 8 */,
('Stephenie', 'Meyer'),
('Jon', 'Krakauer'),
('Frank', 'Herbert'),
('Marie', 'Kondo'),
('Ron', 'Rindo'),
('J.R.R', 'Tolkien'),
('Larry', 'McMurtry'),
('Alex', 'Michaelides');
INSERT INTO bookgenre (book_id, genre_id) values
(2,2),(2,5),
(3,3),(3,5),
(4,4),
(5,5),(5,12),(5,6),
(6,6),(6,4),(6,15),
(7,7),(7,1),(7,17),
(8,8),(8,17),(8,5),(8,10),(8,1),
(9,9),(9,3),(9,11),
(10,10),(10,6),(10,4),
(11,11),(11,9),(11,7),
(12,12),(12,6),(12,5),
(13,13),(13,9),
(14,14),
(15,15),(15,6),(15,5),
(16,16),(16,2),(16,5),
(17,17),(17,1),(17,7),
(1,1),(1,8),(1,17),(1,6);

select b.title, concat(a.first_name, ' ', a.last_name) as 'Author Name', 
GROUP_CONCAT(g.name ORDER BY g.name SEPARATOR ', ') AS genre
From book b
join author a on b.author_id = a.author_id
join bookgenre bg on b.book_id = bg.book_id
join genre g on bg.genre_id = g.genre_id
group by b.book_id
ORDER by b.book_id;


/* Start of the customer part */

create table customer (
	customer_id int primary key auto_increment,
    first_name varchar(100),
    last_name varchar(100),
    email varchar(100),
    phone varchar(10)
);

create table loan (
	loan_id int primary key auto_increment,
    book_id int,
    foreign key (book_id) references book(book_id),
    customer_id int,
    foreign key (customer_id) references customer(customer_id),
    loan_date date,
    due_date date,
    return_date date
);

create table fine (
	fine_id int primary key auto_increment,
    loan_id int,
    foreign key (loan_id) references loan(loan_id),
    amount decimal(5,2),
    paid boolean default false
);

alter table loan
add is_returned boolean default false;

insert into customer (first_name, last_name, email, phone) value
('Jane', 'Doe', 'jane@example.com', '1234567890'),
('John', 'Deer', 'john@example.com', '0987654321');
insert into loan (book_id, customer_id, loan_date, due_date) value
(2,1,curdate(),date_add(curdate(), interval 14 day));
insert into fine (loan_id, amount, paid) values
(1,2.50,false);

select concat(c.first_name, ' ', c.last_name) as customer_name, c.customer_id, b.title, l.loan_date, l.due_date, l.is_returned
from customer c
join loan l on c.customer_id = l.customer_id
join book b on l.book_id = b.book_id
order by c.customer_id;
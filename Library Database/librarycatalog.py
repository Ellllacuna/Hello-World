import mysql.connector
from mysql.connector import Error
from datetime import date, datetime, timedelta





connection = mysql.connector.connect(
    host="localhost",
    user="sqluser",
    password="password",
    database="libraryCatalog"
    )

cursor = connection.cursor()






def get_customer(cursor):
    first_name = input("Enter your first name: ").strip()
    last_name = input("Enter your last name: ").strip()

    cursor.execute("""
            SELECT customer_id, CONCAT(first_name, ' ', last_name) AS full_name
            FROM customer
            WHERE first_name = %s AND last_name = %s;   
                   """, (first_name, last_name))
    return cursor.fetchone()






def view_books(cursor):
    cursor.execute("SELECT b.title, concat(a.first_name, ' ', a.last_name) AS author_name FROM book b "
    "join author a ON b.author_id = a.author_id;")
    books = cursor.fetchall()
    print("\nBooks in catalog:\n")
    for book in books:
        print(f"- {book[0]}")
        print(f"    Author: {book[1]}\n")
        
    input("Press Enter to return to the main menu...")
    return






def veiw_customers(cursor):
    cursor.execute("SELECT CONCAT(first_name, ' ', last_name) as full_name, email, phone FROM customer;")
    customers = cursor.fetchall()
    print("\nAll Patrons:")
    for customer in customers:
        print(f"- Name: {customer[0]}\n    Email: {customer[1]}\n    Phone: {customer[2]}\n")
    input("Press Enter to return to the main menu...")






def add_new_customer(cursor):
    print()
    first_name = input("Enter first name: ")
    last_name = input("Enter last name: ")
    email = input("Enter email: ")
    phone = input("Enter phone number: ")
    cursor.execute("INSERT INTO customer (first_name, last_name, email, phone) VALUES (%s, %s, %s, %s);",
                   (first_name, last_name, email, phone))
    print(f"\nNew patron {first_name} {last_name} added successfully.\n")
    input("Press Enter to return to the main menu...")






def borrow_book(cursor):
    print()
    customer = get_customer(cursor)

    if not customer:
        print("\nPatron not found. Please register as a new patron first.\n")
        input("Press Enter to return to the main menu...")
        return
    
    customer_id, full_name = customer
    print(f"\nWelcome back, {full_name}!\n")

    search_term = input("Search for a book title or author: ")
    search_term = f"%{search_term}%"

    query = """
    SELECT b.book_id, b.title,  CONCAT(a.first_name, ' ', a.last_name) AS author_name
    FROM book b
    JOIN author a ON b.author_id = a.author_id
    WHERE b.title LIKE %s OR CONCAT(a.first_name, ' ', a.last_name) LIKE %s;
    """

    cursor.execute(query, (search_term, search_term))
    results = cursor.fetchall()

    if not results:
        print("\nNo books found matching your search.")
    else:
        for i, (book_id, title, author) in enumerate(results, start=1):
            print(f"\n{i} Title: {title} | Author: {author}")
    
    choice = int(input("\nEnter the number of the book you want to borrow (0 to cancel): "))
    if choice == 0:
        print("\nBorrowing cancelled.\n")
        return
    elif 1 <= choice <= len(results):
        selected_book = results[choice - 1]
        book_id, title, author = selected_book

        #checking to see if book is already loaned out
        cursor.execute("""
            SELECT loan_id FROM loan
            WHERE book_id = %s AND is_returned = FALSE;
                       """, (book_id,))
        active_loan = cursor.fetchone()

        if active_loan:
            print(f"\nSorry, '{title}' by {author} is currently loaned out. Please choose another book.\n")
            input("Press Enter to return to the main menu...")
            return

        loan_date = date.today()
        due_date = loan_date + timedelta(days=14)
        cursor.execute("""
                INSERT INTO loan (book_id, customer_id, loan_date, due_date) 
                VALUES (%s, %s, %s, %s);
                """, (book_id, customer_id, loan_date, due_date))
        
        loan_id = cursor.lastrowid
        
        print(f"\nYou have successfully borrowed '{title}' by {author}.")
        print(f"Loan Date: {loan_date}, Due Date: {due_date}\n")
        print(f"Your loan id is {loan_id}. Please keep it for your records.\n")
        input("Press Enter to return to the main menu...")
        return
    else:
        print("\nInvalid selection. Please try again.\n")





def return_book(cursor):
    print()
    customer = get_customer(cursor)

    if not customer:
        print("\nPatron not found. Please register as a new patron first.\n")
        input("Press Enter to return to the main menu...")
        return

    customer_id, full_name = customer
    print(f"\nWelcome back, {full_name}!\n")

    cursor.execute("""
        SELECT l.loan_id, b.title, l.loan_date, l.due_date,
        CONCAT(a.first_name, ' ', a.last_name) AS author_name
        FROM loan l
        JOIN book b ON l.book_id = b.book_id
        JOIN author a ON b.author_id = a.author_id
        WHERE l.customer_id = %s AND l.is_returned = FALSE;
                   """,(customer_id,))
    
    loans = cursor.fetchall()

    if not loans:
        print("You have no books to return.\n")
        return
    else:
        print("Your current loans: ")
        for i, (loan_id, title, loan_date, due_date, author_name) in enumerate(loans, start=1):
            print(f"\n{i}.  Loan ID: {loan_id}\n    Title: {title}\n    Author: {author_name}\n    Loan Date: {loan_date}\n    Due Date: {due_date}")

    choice = int(input("\nEnter the number of the book you want to return (0 to cancel): "))
    if choice == 0:
        print("\nReturn cancelled.\n")
        return
    elif 1 <= choice <= len(loans):
        selected_loan_id = loans[choice - 1][0]

        cursor.execute("""
            UPDATE loan
            SET is_returned = TRUE, return_date = CURDATE()
            WHERE loan_id = %s;
                       """, (selected_loan_id,))
        print(f"\nYou have successfully returned this book. Thank you!\n")
        return
    else:
        print("\nInvalid selection. Please try again.\n")






def view_fines(cursor):
    print()
    customer = get_customer(cursor)

    if not customer:
        print("\nPatron not found. Please register as a new patron first.\n")
        input("Press Enter to return to the main menu...")
        return
    
    customer_id, full_name = customer
    print(f"\nWelcome back, {full_name}!\n")

    # cursor.execute("""
    #     SELECT f.fine_id, f.amount, f.paid, l.customer_id, l.due_date, b.title
    #                FROM fine f
    #                JOIN loan l on f.loan_id = l.loan_id
    #                JOIN book b ON l.book_id = b.book_id
    #                WHERE l.customer_id = %s AND f.paid = FALSE;
    #                """, (customer_id,))
    cursor.execute("""
        SELECT l.loan_id, b.title, l.due_date, l.return_date, f.paid, f.fine_id
                   FROM loan l
                   JOIN book b ON l.book_id = b.book_id
                   LEFT JOIN fine f ON l.loan_id = f.loan_id
                   WHERE l.customer_id = %s AND (
                        (l.return_date IS NULL AND l.due_date < CURDATE()) OR
                        (l.return_date IS NOT NULL AND l.return_date > l.due_date)
                   )
                   AND (f.paid = FALSE OR f.paid IS NULL);
                   """, (customer_id,))
    
    fines = cursor.fetchall()

    if not fines:
        print("You have no outstanding fines.\n")
        input("Press Enter to return to the main menu...")
        return
    
    today = date.today()
    total_fine = 0
    
    print("Overdue books and fines: \n")
    #for fine in fines:
        #print(f"- Fine ID: {fine[0]}, Amount: ${fine[1]:.2f}, Book Title: {fine[5]}, Paid: {'Yes' if fine[2] else 'No'}")
        #input("\nPress Enter to return to the main menu...")
    
    for loan_id, title, due_date, return_date, paid, fine_id in fines:
        if return_date and return_date > due_date:
            days_late = (return_date - due_date).days
        elif not return_date and due_date < today:
            days_late = (today - due_date).days
        else:
            days_late = 0

        if days_late > 0:
            fine_amount = (days_late * 1.00) + 5.00
            total_fine += fine_amount

        print(f"- Title: {title}\n  Due Date: {due_date}\n  Days Late: {days_late}\n  Fine Amount: ${fine_amount:.2f}\n  Fine ID: {fine_id}\n")
        print(f"Total Fine Amount: ${total_fine:.2f}")

        # Check if a fine already exists for this loan
        cursor.execute("""
            SELECT fine_id FROM fine WHERE loan_id = %s;
                       """,(loan_id,))
        existing_fine = cursor.fetchone()

        if existing_fine:
            cursor.execute("""
                UPDATE fine
                SET amount = %s, paid = FALSE
                WHERE loan_id = %s;
                           """,(fine_amount, loan_id))
        else:
            cursor.execute("""
                INSERT INTO fine (loan_id, amount)
                VALUES (%s, %s);
                           """,(loan_id, fine_amount))
    
    #time for payment
    print("1. Make a payment.")
    print("2. Return to main menu.")
    choice = input("Choose an option (1-2): ")
    if choice == "1":
        fine_choice = int(input("Enter the ID of the fine you wish to pay: "))
        if fine_choice in [fine[5] for fine in fines if fine[5] is not None]:
            cursor.execute("""
                UPDATE fine
                SET paid = TRUE
                WHERE fine_id = %s;
                           """, (fine_choice,))
            print("\nThank you for your payment. Your fine has been marked as paid.\n")
            input("Press Enter to return to the main menu...")
            return
        else:
            print("\nInvalid fine ID. Please try again.\n")
            input("Press Enter to return to the main menu...")
            return
    else: 
        print("\nReturning to main menu.\n")
        return

    
    



def main():

    quit = False

    while not quit:

        print("\n=== Library Menu ===")
        print("1. View Books")
        print("2. View All Patrons")
        print("3. Add New Patron")
        print("4. Borrow a Book")
        print("5. Return a Book")
        print("6. View/Pay Fines")
        print("7. Quit")

        userinput = input("Choose an option (1-7): ")
        
        if userinput == "1":
            view_books(cursor)
        elif userinput == "2":
            veiw_customers(cursor)
        elif userinput == "3":
            add_new_customer(cursor)
            connection.commit()
        elif userinput == "4":
            borrow_book(cursor)
            connection.commit()
        elif userinput == "5":
            return_book(cursor)
            connection.commit()
        elif userinput == "6":
            view_fines(cursor)
            connection.commit()
        else:
            print("\nThank you for using the library catalog system.\n")
            quit = True


if __name__ == "__main__":
    main()
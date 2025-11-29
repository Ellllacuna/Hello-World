# Overview
This web application allows users to upload and store files. It also tracks upload actvity and statistics. It uses Django to handle routing, data storage, and server-side logic.

To start the web app, make sure that you are in the fileManagement folder, then run py (or python) manage.py runserver. This will start up the server. To access the app itself, go to 127.0.0.1:8000. That should bring you to the login page.

My purpose for creating this web app was to gain experience with Django in general. It was also a good example of how user mananagement works.

[Software Demo Video](https://youtu.be/eI_Q5xGaD3E)

# Web Pages

When you go to 127.0.0.1:8000, it will automatically direct you to the login page. Here you can log in with an existing account, or you can click the 'Sign Up' link to take you to the signup form. I used the general Django signup form here, so it just asks for a username and password. It handles the creation and security of the accounts on its own.

Once you are able to log in, it takes you to the Dashboard page. If you have uploaded any files, they would be listed here, and you would have the option to download, view, or delete them. It has links to your user profile, upload page, and a logout button. The logout button will just take you back to the login screen. Upload File will take the user to /upload/, where they can upload a file or go back to the dashboard.

The profile page has the most information. It has links to the dashboard and logout pages, and also the statistics of each user. It displays the total files uploaded, the total storage used, upload streak, and the most recent upload. At the botton of the page is an upload activity chart. It displays the amount of files the user has uploaded per day in the form of a bar graph.

# Development Environment
- Django
- VS studio code

- HTML
- CSS
- Python

# Useful Websites

{Make a list of websites that you found helpful in this project}
* [Django Web App Creation Tutorial](https://docs.djangoproject.com/en/5.2/intro/tutorial01/)
* [Django Official Documentation](https://docs.djangoproject.com/en/5.2/)

# Future Work

* Allow users to rename their files
* A search bar. So that prolific users have an easier time finding their files
* Implement file categories, like photos, videos, ect..
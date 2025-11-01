# Overview


This software allows users to view, edit, and share playlist that are stored in a Firebase database. Running the python program will bring up a list of options that the user can use to interact with, change, and share music playlists.

It demonstrates how Python can be used to interact with a cloud based database. Every change made with the python code will reflect on the actual state of the database in real time. This would allow multiple people to work on the database at the same time if they so desired.

[Software Demo Video](https://www.youtube.com/watch?v=OVgPHim6zZI)

# Cloud Database


This cloud database uses Firestore Firebase. It is a serverless, cloud-based NoSQL database.

Because this database is NoSQL, there are no traditional tables and data rows. There is one collection of playlists. Each playlist is identified by an auto generated document id, and contains identifing information such as the playlist name, owner, share id, and song information.

# Development Environment


- VS Studio Code
- Google's Firestore Cloud Database
- Firebase_admin python Library
- google.cloud.firestore Library


- Python

# Useful Websites


- [Firebase Fundamentals Documentation](https://firebase.google.com/docs/guides)
- [Firestore Code Samples](https://cloud.google.com/firestore/docs/samples)

# Future Work

- Improve the sharability of the playlists
- Create a user log in, so only the owner of the playlist can change their lists
- Find a way to stop the warnings from printing every time the code interacts with the database 
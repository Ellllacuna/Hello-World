import firebase_admin
from firebase_admin import credentials, firestore, db
import os
from google.cloud.firestore_v1.base_query import FieldFilter, Or

#to get rid of the log message when commiting. Nevermind. Does not work. safe to ignore
os.environ["GRPC_VERBOSITY"] = "ERROR"
os.environ["GRPC_CPP_LOG_LEVEL"] = "ERROR"



cred = credentials.Certificate("playlist-manager-9ad47-firebase-adminsdk-fbsvc-a21a172315.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

#helper function to find playlists matching a name and returning them as a list
def find_playlist():  
    #hopefully will make it so that you can search parts of a playlist name or owner
    search_term = input("Enter the name or owner of the playlist: ").lower()

    all_playlists = db.collection("playlists").stream()

    playlists = []
    for p in all_playlists:
        data = p.to_dict()
        name = data['name'].lower()
        owner = data['owner'].lower()

        if search_term in name or search_term in owner:
            playlists.append(p)

    
    return playlists

def add_playlist():
    name = input("Enter playlist name: ")
    owner = input("Enter your name: ")
    songs = []

    while True:
        title = input("\nEnter a song title (Press Enter to cancel): ")
        if title == "":
            break
        artist = input("Enter artist name: ")
        print()
        songs.append({"title": title, "artist": artist})

    doc_ref = db.collection("playlists").document()
    doc_ref.set({
        "name": name,
        "owner": owner,
        "songs": songs
    })
    print(f"Playlist '{name}' added.")

def get_playlists():
    print("\n All playlists:\n")
    playlists = db.collection("playlists").stream()
    for i,p in enumerate(playlists, start=1):
        data = p.to_dict()
        print(f"{i} {data['name']} by {data['owner']}")
        for song in data["songs"]:
            print(f"    {song['title']} - {song['artist']}")

        print()

    input("\nPress Enter to return to the menu...")
    return

def search_playlists():
    playlists = find_playlist()

    if not playlists:
        input("\nNo matching Playlists. Press Enter to return to the main menu.")
        return

    for i,p in enumerate(playlists, start = 1):
        data = p.to_dict()
        songs = data.get("songs", [])
        print(f"{i}. {data['name']} by {data['owner']}")
        for song in songs:
            print(f"    {song['title']} - {song['artist']}")
        
        print()
    
    input("\nPress Enter to return to the menu...")
    return


def add_song_to_playlists():
    playlists = find_playlist()

    if not playlists:
        input("No matching Playlists. Press Enter to return to the main menu")
        return

    print("\nMatching Playlists:\n")
    for i,p in enumerate(playlists, start=1):
        data = p.to_dict()
        print(f"{i}. {data['name']} by {data['owner']}")

    choice = int(input("\nEnter the number of the playlist to edit: "))

    if 1 <= choice <= len(playlists):
        chosen = playlists[choice - 1]

        title = input('\nEnter song title: ')
        artist = input("Enter artist name: ")
        print()
        new_song = {"title": title, "artist": artist}

        db.collection("playlists").document(chosen.id).update({
            "songs": firestore.ArrayUnion([new_song])
        })

        print(f"Added '{title}' to '{chosen.to_dict()['name']}'")
    else:
        print("Invalid choice")

def delete_song_from_playlist():
    playlists = find_playlist()

    if not playlists:
        input("No matching Playlists. Press Enter to return to the main menu.")
        return
    
    print("\nMatching Playlists:\n")
    for i,p in enumerate(playlists, start=1):
        data = p.to_dict()
        print(f"{i}. {data['name']} by {data['owner']}")
        choice = int(input("\n Enter the number of the playlist you want to modify: "))

        if 1<= choice <= len(playlists):
            chosen = playlists[choice - 1]
            data = chosen.to_dict()
            songs = data.get("songs", [])

            if not songs:
                input("No songs in this Playlist. Press Enter to return to the main menu.")
                return
            
            for i,song in enumerate(songs, start=1):
                print(f"{i}. {song["title"]} - {song["artist"]}")
            
            song_choice = int(input("\nEnter the number of the song to delete: "))
            
            if 1 <= song_choice <= len(songs):
                song_to_delete = songs[song_choice - 1]
                db.collection("playlists").document(chosen.id).update({
                    "songs": firestore.ArrayRemove([song_to_delete])
                })
                print(f"Deleted '{song_to_delete.to_dict()['title']}' from '{data['name']}'")
            else:
                input("Invalid song choice, Press Enter to return to the main menu.")
                return
        else:
            input("Invalid Playlist choice. Press Enter to return to the main menu.")
            return

def delete_playlist():
    playlists = find_playlist()
    
    if not playlists:
        print("No playlists found with that name.")
        return

    print("\nMatching Playlists:")
    for i, p in enumerate(playlists, start=1):
        data = p.to_dict()
        print(f"{i}. {data['name']} by {data['owner']} (ID: {p.id})")
        choice = int(input("\n Enter in the number of the playlist you want to delete: "))

        if 1 <= choice <= len(playlists):
            chosen = playlists[choice - 1]
            db.collection("playlists").document(chosen.id).delete()
            print(f"Deleted playlist '{chosen.get_dict()['name']}' (owned by {chosen.to_dict()['owner']})")
        else:
            print("invalid choice")

def main():
    while True:
        print("\n=== Playlist Manager ===")
        print("1. Add Playlist")
        print("2. View All Playlists")
        print("3. Search Playlists")
        print("4. Add Song to Playlist")
        print("5. Delete Song from Playlist")
        print("6. Delete Playlist")
        print("7. Exit")

        choice = input("Choose an option: ")

        if choice == "1":
            add_playlist()
        elif choice == "2":
            get_playlists()
        elif choice == "3":
            search_playlists()
        elif choice == "4":
            add_song_to_playlists()
        elif choice == "5":
            delete_song_from_playlist()
        elif choice == "6":
            delete_playlist()
        elif choice == "7":
            print("Thank you for using the Playlist Manager!")
            break
        else:
            print("Invalid option.")

if __name__ == "__main__":
    main()
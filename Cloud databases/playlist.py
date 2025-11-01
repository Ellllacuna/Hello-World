import firebase_admin
from firebase_admin import credentials, firestore, db
import os
from google.cloud.firestore_v1.base_query import FieldFilter, Or
#gor generating sharable playlist codes
import random
import string
#for listening to changes in the database
import threading
import time

#to get rid of the log message when commiting. Nevermind. Does not work. safe to ignore
os.environ["GRPC_VERBOSITY"] = "ERROR"
os.environ["GRPC_CPP_LOG_LEVEL"] = "ERROR"


#credentials with secret json file :O
cred = credentials.Certificate("playlist-manager-9ad47-firebase-adminsdk-fbsvc-a21a172315.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

first_snapshot = True

# function for listening to changes in the database
def on_playlist_change(col_snapshot, changes, read_time):
    global first_snapshot

    #skips first snapshot to avoid duplicate messages
    if first_snapshot:
        first_snapshot = False
        return

    print("\n=== Playlist Database Updated ===\n")
    for change in changes:
        #if the change is an addition of a new playlist
        if change.type.name == 'ADDED':
            print(f"New playlist added: {change.document.to_dict()['name']}")
        #if the change is a modification of an existing playlist
        elif change.type.name == 'MODIFIED':
            print(f"Playlist modified: {change.document.to_dict()['name']}")
        #if the change is a deletion of a playlist
        elif change.type.name == 'REMOVED':
            print(f"Playlist removed: {change.document.to_dict()['name']}")
    print("\nPress ENTER to refresh or continue your action...")

#start listener function
def start_listener():
    print("Listening for playlist changes...")
    db.collection("playlists").on_snapshot(on_playlist_change)

#helper function to find playlists matching a name and returning them as a list
def find_playlist():  
    #hopefully will make it so that you can search parts of a playlist name or owner
    search_term = input("Enter the name or owner of the playlist (Press Enter to cancel): ").lower()
    if search_term == "":
        return
    
    else:
        
        all_playlists = db.collection("playlists").stream()

        playlists = []
        for p in all_playlists:
            data = p.to_dict()
            name = data['name'].lower()
            owner = data['owner'].lower()

            if search_term in name or search_term in owner:
                playlists.append(p)

        
        return playlists

#generate sharable code for playlists (6 characters long)   
def generate_code():
    return "".join(random.choices(string.ascii_letters + string.digits, k=6))

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
    
    share_id = generate_code()

    doc_ref = db.collection("playlists").document()
    doc_ref.set({
        "name": name,
        "owner": owner,
        "songs": songs,
        "share_id": share_id
    })
    print(f"Playlist '{name}' added.")
    print(f"Shareable code: {share_id}")


def view_shared_playlist():
    code = input("Enter the share code of the playlist: ").strip()
    if not code:
        print("No code entered.")
        return
    
    results = db.collection("playlists").where("share_id", "==", code).limit(1).stream()
    #saves the first result found with the matching share code

    playlist = None
    for r in results:
        playlist = r.to_dict()
        break

    if not playlist:
        print("No playlist foundw with that share code.")
        return
    
    print(f"\nPlaylist: {playlist['name']} by {playlist['owner']}")
    print("Songs:")
    for song in playlist["songs"]:
        print(f" - {song['title']} by {song['artist']}")
    print()
    input("Press Enter to return to the menu...")
    return

#return the share code of already existing playlists
def get_share_code():
    playlist = find_playlist()

    for i,p in enumerate(playlist, start=1):
        data = p.to_dict()
        print(f"\n{i}. {data['name']} by {data['owner']}")
        print(f"Share code: {data['share_id']}\n")
    
    print()
    input("Press Enter to return to the menu...")
    return

def get_playlists():
    #not included in find_playlists function because it does not need a search term
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
                print(f"Deleted '{song_to_delete['title']}' from '{data['name']}'")
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
            print(f"Deleted playlist '{chosen.to_dict()['name']}' (owned by {chosen.to_dict()['owner']})")
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
        print("7. Search Playlist by Share Code")
        print("8. Get Share Code for Playlist")
        print("9. Exit")

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
            view_shared_playlist()
        elif choice == "8":
            get_share_code()
        elif choice == "9":
            print("Thank you for using the Playlist Manager!")
            break
        else:
            print("\n=================================")


if __name__ == "__main__":
    #use threads to run the listener in the background
    listener_thread = threading.Thread(target=start_listener, daemon=True)
    listener_thread.start()
    time.sleep(0.5) #help clear up confusing print order

    print("\n=================================")
    print("Firestore Listener is active!")
    print("\n=================================")
    input("Press Enter to start the Playlist Manager...")

    main()
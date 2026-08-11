# ==========================================
# Import Required Libraries
# ==========================================

import json 
from pathlib import Path
import webbrowser

# ==========================================
# Recommended Counter variables
# ==========================================

skip_counter = 0
remove_from_keep = 0
added_to_keep = 0

# ==========================================
# Helper Functions
# ==========================================

# Loads usernames from follower text file
def load_followers(file_path):
    """Read followers_1.json and return the usernames as a set."""

    with open(file_path, "r") as file:
        data = json.load(file)

    followers = set()

    for follower in data:
        username = follower["string_list_data"][0]["value"]
        followers.add(username)

    return followers

# Loads usernames from following text file with name and url
def load_following(file_path):
    """Return a dictionary mapping each username to its profile URL."""

    with open(file_path, "r") as file:
        data = json.load(file)

    following = {}

    for person in data["relationships_following"]:
        url = person["string_list_data"][0]["href"]
        username = url.rstrip("/").split("/")[-1]
        
        if username == "":
            print("Problem entry:")
            print(person)
            print()
        else:
            following[username] = url

    return following

# Loads a list of usernames to continue following despite no reciprocation
def load_keep_list(file_path):
    """Read approved usernames from a text file and return them as a set."""

    if not file_path.exists():
        return set()

    with open(file_path, "r") as file:
        keep_following = set()

        for line in file:
            username = line.strip().lower()

            if username:
                keep_following.add(username)

    return keep_following

# Reviews accounts, updates keep_following.txt, and generates the review list.
def update_keep_following(review_list, following_profiles, keep_file, stale_usernames, review_file, old_following_profiles):
    """Ask the user which accounts to keep following."""

    global skip_counter, remove_from_keep, added_to_keep
    keep_following = load_keep_list(keep_file)
    review_output = []

    for username in sorted(stale_usernames):
        print()
        print("========== Remove From Keep List ==========")
        print()
        print(f"You no longer follow: {username}")

        if username in old_following_profiles:
            print(old_following_profiles[username])
        answer = input("Remove from keep_following.txt? (y/n): ").lower()
        while answer not in ("y", "n"):
            answer = input("Invalid input. Enter y or n: ").lower()

        if answer == "y":
            remove_from_keep += 1
            keep_following.remove(username)
            print(f"Removed {username}. Updated keep_following.txt successfully.")

    for username in sorted(review_list):
        print()
        print("========== Review Account ==========")
        print()
        print(f"Username: {username}")
        print(f"Profile: {following_profiles[username]}")
        answer = input(f"Keep following {username}? (y/n/s): ").lower()
        while answer not in ("y", "n", "s"):
            answer = input("Invalid input. Please enter 'y', 'n', or 's': ").lower()
        if answer == "y":
                keep_following.add(username)
                added_to_keep += 1
                print(f"Added {username} to keep_following.txt")
        elif answer == "s":
            skip_counter += 1
            review_output.append(f"[SKIP] {username}")
            review_output.append(following_profiles[username])
            review_output.append("")
            print(f"Skipped {username}. It will be reviewed again next run.")
        else:  #answer == n
            review_output.append(f"[REVIEW] {username}")
            review_output.append(following_profiles[username])
            review_output.append("")

    with open(keep_file, "w") as file:
        for username in sorted(keep_following):
            file.write(username + "\n")

    with open(review_file, "w") as file:
        file.write("\n".join(review_output))
# Displays Letter Explanations
def letter_explanations():
    print()
    print("y = Keep permanently")
    print("n = Ask again next time")
    print("s = Skip this run only")
    print()

# Checks if file exists
def verify_file(file_path, description):
    if not file_path.exists():
        print(f"Error: {description} not found.")
        exit()

# ==========================================
# Main program
# ==========================================

project_folder = Path(__file__).parent

# Creates necessary files
old_followers_file = (
    project_folder / "data" / "export_0" / "followers_1.json"
)
old_following_file = (
    project_folder / "data" / "export_0" / "following.json"
)
new_followers_file = (
    project_folder / "data" / "export_1" / "followers_1.json"
)
new_following_file = (
    project_folder / "data" / "export_1" / "following.json"
)
keep_file = project_folder / "data" / "keep_following.txt"
review_file = project_folder / "output" / "review_list.txt"

# Verify required files exist
verify_file(old_followers_file, "export_0 followers_1.json")
verify_file(old_following_file, "export_0 following.json")
verify_file(new_followers_file, "export_1 followers_1.json")
verify_file(old_followers_file, "export_0 following.json")
verify_file(keep_file, "keep_following.txt")

# Load Instagram data
old_followers = load_followers(old_followers_file)
old_following_profiles = load_following(old_following_file)
new_followers = load_followers(new_followers_file)
new_following_profiles = load_following(new_following_file)

# Build follower and following sets
old_following_usernames = set(old_following_profiles.keys())
new_following_usernames = set(new_following_profiles.keys())
old_not_following_back = old_following_usernames - old_followers
new_not_following_back = new_following_usernames - new_followers

# Generate keep list
generated_keep_following = old_not_following_back & new_not_following_back
saved_keep_following = load_keep_list(keep_file)
keep_following = generated_keep_following | saved_keep_following
with open(keep_file, "w") as file:
    for username in sorted(keep_following):
        file.write(username + "\n")
stale_usernames = keep_following - set(new_following_profiles.keys())

# Generate review list
review_list = new_not_following_back - keep_following
print("Generated keep list count:", len(keep_following))

#Formatting
letter_explanations()

# Update keep following list
update_keep_following(
    review_list,
    new_following_profiles,
    keep_file,
    stale_usernames,
    review_file,
    old_following_profiles
)

# Sort review list
sorted_usernames = sorted(review_list)

# Display summary
print()
print("========== Summary ==========")
print()
print(f"Reviewed: {len(sorted_usernames)} accounts")
print(f"Added to keep list: {added_to_keep}")
print(f"Skipped this run: {skip_counter}")
print(f"Left for future review: {len(review_list)}")
print(f"Removed from keep list: {remove_from_keep}")

print(f"Results saved to: {review_file}")
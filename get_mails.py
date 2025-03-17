#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "click",
#     "requests",
# ]
# ///
import click
import requests
import sys
from datetime import datetime
import os


class ElabFTW:
    """Class for interacting with an ElabFTW server."""

    session = None
    host_url = None

    def __init__(self, host_url, apikey, user_agent_string="get_user_mails"):
        """
        Initialize an instance of the ElabFTW class.

        Args:
            host_url (str): The URL of the ElabFTW server.
            apikey (str): The API key used for authentication.

        """
        print("Initializing ElabFTW class with user_agent_string: " + user_agent_string)
        self.host_url = host_url
        # normalize self.host_url to remove everything after the last TLD ending
        # e.g. https://elabftw.example.com/login -> https://elabftw.example.com
        self.host_url = host_url.rsplit("/", 1)[0]
        self.session = requests.Session()
        self.session.headers.update(
            {"Authorization": apikey, "User-Agent": user_agent_string}
        )
        self.all_users = None
        self.user_data_list = None

    def check_connection(self):
        """Check if the connection to ElabFTW is working.

        Return True if the connection is working, otherwise raises a critical error and exits the script.
        """
        try:
            resp = self.session.get(self.host_url + "/api/v2/info")
        except requests.exceptions.ConnectionError:
            print("Error connecting to ElabFTW: Connection refused")
            sys.exit(1)
        else:
            if resp.status_code != 200:
                print(
                    "Error connecting to ElabFTW: "
                    + str(resp.status_code)
                    + " "
                    + resp.text
                )
                sys.exit(1)
            else:
                return True

    def get_all_users(self):
        """Get all users from ElabFTW as JSON."""
        print("Getting all users from ElabFTW...")
        resp = self.session.get(self.host_url + "/api/v2/users?includeArchived=1")
        if resp.status_code != 200:
            print("Error getting users: " + resp.text)
            sys.exit(1)

        return resp.json()

    def get_active_users(self):
        # Filter users with a last_login date
        active_users = [user for user in self.all_users if user.get("last_login")]
        print(f"Number of active users: {len(active_users)}")
        return active_users

    def get_active_team_leaders(self):
        active_users = [user for user in self.all_users if user.get("last_login")]
        user_ids = [user["userid"] for user in active_users]
        user_data_list = []
        active_team_leaders = []
        for user_id in user_ids:
            user_resp = self.session.get(self.host_url + f"/api/v2/users/{user_id}")
            if user_resp.status_code != 200:
                print("Error get user object: " + user_resp.text)
            else:
                user_data_list.append(user_resp.json())

        for user in user_data_list:
            for team in user["teams"]:
                if team["usergroup"] == 2:
                    active_team_leaders.append(user)
                    break
        return active_team_leaders


def connect_to_elabftw(ELABFTW_HOST, ELABFTW_APIKEY):
    # Check if the connection to ElabFTW is working

    elabftw = ElabFTW(ELABFTW_HOST, ELABFTW_APIKEY)

    if elabftw.check_connection():
        print("Connection to ElabFTW successful")
    else:
        print("Connection to ElabFTW failed")

    elabftw.all_users = elabftw.get_all_users()

    print(f"Total number of users: {len(elabftw.all_users)}")
    return elabftw


def save_for_outlook(userlist, type):
    current_date = datetime.now().strftime("%Y-%m-%d")
    with open(f"output/{current_date}_{type}_user_mails_for_outlook.txt", "w") as f:
        f.write(" ; ".join(set([user["email"] for user in userlist])))
    print(
        f"{len(userlist)} mail adresses saved to {current_date}_{type}_user_mails_for_outlook.txt"
    )


def save_to_textfile(userlist, type):
    current_date = datetime.now().strftime("%Y-%m-%d")
    with open(f"output/{current_date}_{type}_user_mails.txt", "w") as f:
        f.write("\n".join(set([user["email"] for user in userlist])))
    print(
        f"{len(userlist)} mail adresses saved to {current_date}_{type}_user_mails.txt"
    )


@click.command()
def start():
    output_dir = os.path.join(os.path.dirname(__file__), "output")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    ELABFTW_HOST = click.prompt(
        "Please enter the URL to your elabFTW Instance", type=str
    )

    ELABFTW_APIKEY = click.prompt("Please enter your API key", type=str)
    elabftw = connect_to_elabftw(ELABFTW_HOST, ELABFTW_APIKEY)

    team_leaders_or_all_users = click.prompt(
        "Do you want to get all users (1) or only team leaders (2)?", type=int
    )
    if team_leaders_or_all_users == 1:
        print("Getting all active users...")
        type = "all"
        userlist = elabftw.get_active_users()
    elif team_leaders_or_all_users == 2:
        print("Getting all team leaders...")
        type = "team_leaders"
        userlist = elabftw.get_active_team_leaders()

    saving_option = click.prompt("Save to text file (1) or Outlook (2)?", type=int)
    if saving_option == 1:
        save_to_textfile(userlist, type)
    elif saving_option == 2:
        save_for_outlook(userlist, type)


if __name__ == "__main__":
    start()

#!/usr/bin/python3
"""
This module prints the titles of the ten hottest subreddit posts.
"""

import os
import requests


def _get_access_token():
    """Returns an OAuth access token from Reddit."""
    client_id = os.environ.get("REDDIT_CLIENT_ID")
    client_secret = os.environ.get("REDDIT_CLIENT_SECRET")
    user_agent = os.environ.get("REDDIT_USER_AGENT")

    if not client_id or not client_secret or not user_agent:
        return None

    try:
        response = requests.post(
            "https://www.reddit.com/api/v1/access_token",
            auth=requests.auth.HTTPBasicAuth(
                client_id, client_secret
            ),
            data={"grant_type": "client_credentials"},
            headers={"User-Agent": user_agent}
        )
        if response.status_code != 200:
            return None

        return response.json().get("access_token")
    except (requests.exceptions.RequestException, ValueError):
        return None


def top_ten(subreddit):
    """Prints the titles of the ten hottest posts."""
    token = _get_access_token()

    if not token:
        print("None")
        return

    user_agent = os.environ.get("REDDIT_USER_AGENT")
    url = "https://oauth.reddit.com/r/{}/hot.json".format(
        subreddit
    )

    headers = {
        "Authorization": "bearer {}".format(token),
        "User-Agent": user_agent
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            params={"limit": 10},
            allow_redirects=False
        )

        if response.status_code != 200:
            print("None")
            return

        posts = response.json().get("data", {}).get("children", [])

        if not posts:
            print("None")
            return

        for post in posts[:10]:
            print(post.get("data", {}).get("title", ""))

    except (requests.exceptions.RequestException, ValueError):
        print("None")

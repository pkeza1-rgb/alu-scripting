#!/usr/bin/python3
"""
This module retrieves the number of subscribers for a subreddit.
"""

import os
import requests


def number_of_subscribers(subreddit):
    """Returns the number of subscribers for a subreddit."""
    client_id = os.environ.get("REDDIT_CLIENT_ID")
    client_secret = os.environ.get("REDDIT_CLIENT_SECRET")
    user_agent = os.environ.get("REDDIT_USER_AGENT")

    if not client_id or not client_secret or not user_agent:
        return 0

    try:
        auth_response = requests.post(
            "https://www.reddit.com/api/v1/access_token",
            auth=requests.auth.HTTPBasicAuth(
                client_id, client_secret
            ),
            data={"grant_type": "client_credentials"},
            headers={"User-Agent": user_agent}
        )

        if auth_response.status_code != 200:
            return 0

        token = auth_response.json().get("access_token")

        if not token:
            return 0

        url = "https://oauth.reddit.com/r/{}/about".format(
            subreddit
        )

        headers = {
            "Authorization": "bearer {}".format(token),
            "User-Agent": user_agent
        }

        response = requests.get(
            url,
            headers=headers,
            allow_redirects=False
        )

        if response.status_code != 200:
            return 0

        return response.json().get(
            "data", {}
        ).get("subscribers", 0)

    except (requests.exceptions.RequestException, ValueError):
        return 0

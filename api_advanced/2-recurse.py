#!/usr/bin/python3
"""
This module recursively retrieves all hot subreddit posts.
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


def recurse(subreddit, hot_list=None, after=None, token=None):
    """Recursively retrieves all hot post titles."""
    if hot_list is None:
        hot_list = []

    if token is None:
        token = _get_access_token()

    if not token:
        return None

    user_agent = os.environ.get("REDDIT_USER_AGENT")
    url = "https://oauth.reddit.com/r/{}/hot.json".format(
        subreddit
    )

    headers = {
        "Authorization": "bearer {}".format(token),
        "User-Agent": user_agent
    }

    params = {"limit": 100}

    if after:
        params["after"] = after

    try:
        response = requests.get(
            url,
            headers=headers,
            params=params,
            allow_redirects=False
        )

        if response.status_code != 200:
            return None

        data = response.json().get("data", {})
        posts = data.get("children", [])

        for post in posts:
            title = post.get("data", {}).get("title")
            if title:
                hot_list.append(title)

        next_after = data.get("after")

        if next_after:
            return recurse(
                subreddit,
                hot_list,
                next_after,
                token
            )

        return hot_list if hot_list else None

    except (requests.exceptions.RequestException, ValueError):
        return None

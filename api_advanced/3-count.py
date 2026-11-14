#!/usr/bin/python3
"""
This module recursively counts keyword occurrences in hot posts.
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


def count_words(subreddit, word_list, counts=None,
                after=None, token=None):
    """Recursively counts and prints keyword occurrences."""
    if counts is None:
        counts = {}

    if token is None:
        token = _get_access_token()

    if not token:
        return

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
            return

        data = response.json().get("data", {})
        posts = data.get("children", [])

        for keyword in word_list:
            word = keyword.lower()
            counts.setdefault(word, 0)

        for post in posts:
            title = post.get("data", {}).get("title", "")
            title_words = title.lower().split()

            for keyword in word_list:
                word = keyword.lower()
                counts[word] += title_words.count(word)

        next_after = data.get("after")

        if next_after:
            count_words(
                subreddit,
                word_list,
                counts,
                next_after,
                token
            )
            return

        results = [
            (word, count)
            for word, count in counts.items()
            if count > 0
        ]

        results.sort(key=lambda item: (-item[1], item[0]))

        for word, count in results:
            print("{}: {}".format(word, count))

    except (requests.exceptions.RequestException, ValueError):
        return

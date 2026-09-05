#INF601- Advanced Programming in Python
#Ray Bednara
#Mini Project 1

import os
import requests
from dotenv import load_dotenv

load_dotenv()

BASE = "https://practice.fhsucyber.com"
TOKEN = os.environ.get("API_KEY")


class PracticeHubClient:
    def __init__(self, base_url, token):
        self.base = base_url.rstrip("/")
        self.headers = {"Authorization": f"Bearer {token}"}

    _ERROR_LABELS = {
        400: "Bad request",
        401: "Unauthorized",
        402: "Payment required",
        403: "Forbidden",
        404: "Not found",
        422: "Unprocessable entity",
    }

    def _check_response(self, resp):
        label = self._ERROR_LABELS.get(resp.status_code)
        if label:
            try:
                detail = resp.json().get("message", resp.text)
            except ValueError:
                detail = resp.text
            raise ValueError(f"{label} ({resp.request.method} {resp.request.url}): {detail}")
        resp.raise_for_status()

    def create_post(self, title, body="", tags=None):
        resp = requests.post(f"{self.base}/api/v1/posts", headers=self.headers,
                             json={"title": title, "body": body, "tags": tags or []})
        self._check_response(resp)
        return resp.json()

    def list_posts(self, mine=False, tag=None):
        params = {"mine": mine}
        if tag:
            params["tag"] = tag
        resp = requests.get(f"{self.base}/api/v1/posts", headers=self.headers, params=params)
        self._check_response(resp)
        return resp.json()

    def get_post(self, post_id):
        resp = requests.get(f"{self.base}/api/v1/posts/{post_id}", headers=self.headers)
        self._check_response(resp)
        return resp.json()

    def update_post(self, post_id, title=None, body=None, tags=None):
        payload = {}
        if title is not None:
            payload["title"] = title
        if body is not None:
            payload["body"] = body
        if tags is not None:
            payload["tags"] = tags
        resp = requests.patch(f"{self.base}/api/v1/posts/{post_id}", headers=self.headers,
                              json=payload)
        self._check_response(resp)
        return resp.json()

    def delete_post(self, post_id):
        resp = requests.delete(f"{self.base}/api/v1/posts/{post_id}", headers=self.headers)
        self._check_response(resp)
        return resp.status_code == 204 or resp.json()


if __name__ == "__main__":
    if not TOKEN:
        raise SystemExit("PRACTICE_API_TOKEN is not set - see 'Set your token' in Week 2.")

    client = PracticeHubClient(BASE, TOKEN)

    try:
        everyone = client.list_posts()
        print(f"posts on the hub: {len(everyone)}")

        new_post = client.create_post("Week 3 lab", body="My first created post.")
        print(f"created post {new_post['id']}: {new_post['title']}")

        print(f"posts that are mine: {len(client.list_posts(mine=True))}")

        fetched = client.get_post(new_post["id"])
        print(f"fetched post {fetched['id']}: {fetched['title']} - {fetched['body']}")

        updated = client.update_post(new_post["id"], title="Week 3 lab (updated)", body="this post is updated", tags=["updated"])
        print(f"updated post {updated['id']}: {updated['title']}")

        deletable_post = client.create_post("Scratch post", body="This post is only here to be deleted.")
        print(f"created post {deletable_post['id']}: {deletable_post['title']}")

        client.delete_post(deletable_post["id"])
        print(f"deleted post {deletable_post['id']}")
    except ValueError as e:
        print(f"request failed: {e}")

    # unhappy path: the post above no longer exists, so this should 404
    try:
        client.get_post(deletable_post["id"])
    except ValueError as e:
        print(f"expected failure fetching deleted post: {e}")
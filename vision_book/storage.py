"""Storage for the Vision Book.

Two layers:
1. A local JSON file (data/vision_book.json) — always written, fast.
2. Optional, durable cloud storage in a PRIVATE GitHub repository.
   Streamlit Cloud wipes local files on every restart or update, so online
   the cloud layer is what keeps your journal safe.

Configure the cloud layer in Streamlit secrets:

    [storage]
    github_token = "github_pat_..."          # fine-grained token, Contents: read & write
    github_repo  = "your-name/vision-book-data"  # a PRIVATE repository
    # optional:
    branch = "main"
    path   = "vision_book.json"
"""
import base64
import copy
import json
import os
import tempfile
from pathlib import Path

import requests

DATA_DIR = Path(os.environ.get("VISION_BOOK_DATA", Path(__file__).resolve().parent.parent / "data"))
DATA_FILE = DATA_DIR / "vision_book.json"
IMAGE_DIR = DATA_DIR / "images"
API = os.environ.get("VISION_BOOK_GITHUB_API", "https://api.github.com")


class SaveError(Exception):
    pass


# ---------------------------------------------------------------------------
# Local file
# ---------------------------------------------------------------------------
def _load_local() -> dict:
    if DATA_FILE.exists():
        try:
            return json.loads(DATA_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            DATA_FILE.replace(DATA_FILE.with_suffix(".corrupt.json"))
    return {}


def _save_local(data: dict) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=DATA_DIR, suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    os.replace(tmp, DATA_FILE)


# ---------------------------------------------------------------------------
# Private GitHub repository
# ---------------------------------------------------------------------------
class GitHubStore:
    def __init__(self, token, repo, branch="main", path="vision_book.json"):
        self.repo, self.branch, self.path = repo, branch, path
        self.s = requests.Session()
        self.s.headers.update({"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json",
                               "X-GitHub-Api-Version": "2022-11-28"})

    def _url(self, path):
        return f"{API}/repos/{self.repo}/contents/{path}"

    def check(self) -> str:
        """Return '' when everything is fine, otherwise a human explanation."""
        r = self.s.get(f"{API}/repos/{self.repo}", timeout=15)
        if r.status_code in (401, 403):
            return "The GitHub token is not accepted. Check that it hasn't expired and has access to this repository."
        if r.status_code == 404:
            return f"Repository '{self.repo}' not found, or the token has no access to it."
        if r.ok and not r.json().get("private", False):
            return f"Repository '{self.repo}' is PUBLIC. Your journal must live in a private repository."
        return "" if r.ok else f"GitHub answered {r.status_code}."

    def get(self):
        """Return (data, sha). sha is None when the file doesn't exist yet."""
        r = self.s.get(self._url(self.path), params={"ref": self.branch}, timeout=20)
        if r.status_code == 404:
            return {}, None
        if not r.ok:
            raise SaveError(f"Could not read your book from GitHub ({r.status_code}).")
        meta = r.json()
        if meta.get("content"):
            raw = base64.b64decode(meta["content"])
        else:  # files over 1 MB come without inline content
            rr = self.s.get(self._url(self.path), params={"ref": self.branch}, timeout=30,
                            headers={"Accept": "application/vnd.github.raw"})
            rr.raise_for_status()
            raw = rr.content
        return json.loads(raw.decode("utf-8") or "{}"), meta["sha"]

    def put(self, path, content: bytes, sha, message):
        body = {"message": message, "content": base64.b64encode(content).decode(), "branch": self.branch}
        if sha:
            body["sha"] = sha
        return self.s.put(self._url(path), json=body, timeout=30)

    def read_bytes(self, path) -> bytes:
        r = self.s.get(self._url(path), params={"ref": self.branch}, timeout=30,
                       headers={"Accept": "application/vnd.github.raw"})
        r.raise_for_status()
        return r.content


# ---------------------------------------------------------------------------
# The Book store used by the app
# ---------------------------------------------------------------------------
class BookStore:
    """Keeps a 'base' snapshot of what was last synced so that edits from two
    devices (phone + laptop) are merged per field instead of overwriting."""

    def __init__(self, cfg: dict | None):
        self.cloud = None
        self.problem = ""
        if cfg and cfg.get("github_token") and cfg.get("github_repo"):
            self.cloud = GitHubStore(cfg["github_token"], cfg["github_repo"],
                                     cfg.get("branch", "main"), cfg.get("path", "vision_book.json"))
            try:
                self.problem = self.cloud.check()
            except requests.RequestException as e:
                self.problem = f"Could not reach GitHub ({e.__class__.__name__})."
        self.sha = None
        self.base = {}

    @property
    def durable(self) -> bool:
        return self.cloud is not None and not self.problem

    def load(self) -> dict:
        local = _load_local()
        if not self.durable:
            self.base = copy.deepcopy(local)
            return local
        remote, self.sha = self.cloud.get()
        if not remote and local:
            # first time connecting: bring what is on this device to the cloud
            remote = local
            self.base = {}
            self.save(remote)
            return remote
        self.base = copy.deepcopy(remote)
        _save_local(remote)
        return remote

    def save(self, data: dict) -> None:
        _save_local(data)
        if not self.durable:
            return
        for _ in range(4):
            content = json.dumps(data, ensure_ascii=False, indent=1).encode("utf-8")
            r = self.cloud.put(self.cloud.path, content, self.sha, "journal update")
            if r.ok:
                self.sha = r.json()["content"]["sha"]
                self.base = copy.deepcopy(data)
                return
            if r.status_code in (409, 422):  # someone (another device) saved in between
                remote, self.sha = self.cloud.get()
                merged = self._merge(remote, data)
                data.clear()
                data.update(merged)
                continue
            raise SaveError(f"GitHub refused the save ({r.status_code}).")
        raise SaveError("Could not save after several attempts.")

    def _merge(self, remote: dict, local: dict) -> dict:
        merged = copy.deepcopy(remote)
        for k in set(local) | set(self.base):
            if k not in local:
                if k in self.base:  # deleted here
                    merged.pop(k, None)
            elif local[k] != self.base.get(k):  # changed here
                merged[k] = local[k]
        return merged

    # images ---------------------------------------------------------------
    def save_image(self, name: str, content: bytes) -> str:
        safe = "".join(c for c in name if c.isalnum() or c in "._-") or "image.png"
        if self.durable:
            path = f"images/{os.urandom(4).hex()}_{safe}"
            r = self.cloud.put(path, content, None, "mood board image")
            if not r.ok:
                raise SaveError(f"Could not upload the image ({r.status_code}).")
            return "gh:" + path
        IMAGE_DIR.mkdir(parents=True, exist_ok=True)
        path = IMAGE_DIR / f"{os.urandom(4).hex()}_{safe}"
        path.write_bytes(content)
        return "file:" + str(path.relative_to(DATA_DIR))

    def image(self, ref: str):
        """Return something st.image can show (url, path or bytes)."""
        if ref.startswith("gh:") and self.cloud:
            return self.cloud.read_bytes(ref[3:])
        if ref.startswith("file:"):
            return str(DATA_DIR / ref[5:])
        return ref

import html
import http.server
import json
import os
import re
import subprocess
import urllib.parse

ROOT = os.path.dirname(os.path.abspath(__file__))
CONTENT_PATH = os.path.join(ROOT, "content.json")

HTML_FILES = [
    "index.html",
    "devin-tucker-site.html",
    "event-videography-portland/index.html",
    "dance-and-performance-film-portland/index.html",
    "video-editing-portland/index.html",
    "now.html",
    "hi.html",
    "404.html",
]


def load_content():
    with open(CONTENT_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def sync_files(data):
    copy_map = data.get("copy", {})
    settings = data.get("settings", {})
    updated_count = 0

    for rel in HTML_FILES:
        fpath = os.path.join(ROOT, rel)
        if not os.path.exists(fpath):
            continue
        with open(fpath, "r", encoding="utf-8") as f:
            orig = f.read()
        txt = orig

        # Replace every data-copy="key">...</
        def repl_copy(m):
            prefix, key, old_val, suffix = m.group(1), m.group(2), m.group(3), m.group(4)
            if key in copy_map:
                new_val = html.escape(str(copy_map[key]), quote=False)
                return f'{prefix}{new_val}{suffix}'
            return m.group(0)

        txt = re.sub(
            r'(data-copy="([^"]+)">)([^<]*)(</)',
            repl_copy,
            txt,
        )

        # Sync SITE settings if present
        if "email" in settings and settings["email"]:
            em = settings["email"].strip()
            txt = re.sub(
                r"(email:\s*)'[^']*'",
                lambda m: f"{m.group(1)}'{em}'",
                txt,
            )
            txt = re.sub(
                r'(data-email-href\s+href="mailto:)[^"]*(")',
                lambda m: f'{m.group(1)}{em}{m.group(2)}',
                txt,
            )
        if "bookingUrl" in settings:
            bu = settings["bookingUrl"].strip()
            txt = re.sub(
                r"(bookingUrl:\s*)'[^']*'",
                lambda m: f"{m.group(1)}'{bu}'",
                txt,
            )
            if bu:
                txt = re.sub(
                    r'(id="book-link"\s+href=")[^"]*(")',
                    lambda m: f'{m.group(1)}{bu}{m.group(2)}',
                    txt,
                )
                txt = re.sub(
                    r'(data-book\s+href=")[^"]*(")',
                    lambda m: f'{m.group(1)}{bu}{m.group(2)}',
                    txt,
                )
        if "formEndpoint" in settings:
            fe = settings["formEndpoint"].strip()
            txt = re.sub(
                r"(formEndpoint:\s*)'[^']*'",
                lambda m: f"{m.group(1)}'{fe}'",
                txt,
            )

        if txt != orig:
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(txt)
            updated_count += 1

    # Sync vCard if email changed
    vcf_path = os.path.join(ROOT, "devin-tucker.vcf")
    if os.path.exists(vcf_path) and settings.get("email"):
        with open(vcf_path, "r", encoding="utf-8") as f:
            vcf = f.read()
        new_vcf = re.sub(
            r"EMAIL;TYPE=INTERNET,WORK:.*",
            f"EMAIL;TYPE=INTERNET,WORK:{settings['email'].strip()}",
            vcf,
        )
        if new_vcf != vcf:
            with open(vcf_path, "w", encoding="utf-8") as f:
                f.write(new_vcf)
            updated_count += 1

    return updated_count


class CopyServerHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def end_headers(self):
        # Prevent browser caching and allow CORS from localhost:8000
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.end_headers()

    def _send_json(self, obj, status=200):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/copy":
            self._send_json(load_content())
            return
        if parsed.path == "/api/git-history":
            try:
                out = subprocess.check_output(
                    ["git", "log", "--all", "-n", "30", "--pretty=format:%h|%ad|%d|%s", "--date=short"],
                    cwd=ROOT,
                    text=True,
                    encoding="utf-8",
                )
                commits = []
                for line in out.strip().splitlines():
                    parts = line.split("|", 3)
                    if len(parts) == 4:
                        ref = parts[2].strip().strip("()")
                        commits.append({
                            "hash": parts[0],
                            "date": parts[1],
                            "ref": ref,
                            "subject": parts[3],
                        })
                self._send_json({"ok": True, "commits": commits})
            except Exception as e:
                self._send_json({"ok": False, "error": str(e)}, 500)
            return
        super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"
        payload = json.loads(raw or "{}")

        if parsed.path == "/api/save-copy":
            data = load_content()
            if "settings" in payload and isinstance(payload["settings"], dict):
                data.setdefault("settings", {}).update(payload["settings"])
                if "email" in payload["settings"]:
                    data.setdefault("copy", {})["global.email"] = payload["settings"]["email"]
            if "copy" in payload and isinstance(payload["copy"], dict):
                data.setdefault("copy", {}).update(payload["copy"])
                if "global.email" in payload["copy"]:
                    data.setdefault("settings", {})["email"] = payload["copy"]["global.email"]

            with open(CONTENT_PATH, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            updated = sync_files(data)
            self._send_json({"ok": True, "updated_files": updated})
            return

        if parsed.path == "/api/git-checkpoint":
            msg = (payload.get("message") or "Update website copy").strip()
            try:
                subprocess.run(["git", "add", "-A"], cwd=ROOT, check=True)
                status = subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True).strip()
                if not status:
                    self._send_json({"ok": False, "error": "No changes since last commit"})
                    return
                subprocess.run(["git", "commit", "-m", msg], cwd=ROOT, check=True)
                short_hash = subprocess.check_output(
                    ["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, text=True
                ).strip()
                pushed = False
                if payload.get("push", True):
                    p = subprocess.run(["git", "push", "origin", "HEAD"], cwd=ROOT)
                    pushed = p.returncode == 0
                self._send_json({"ok": True, "commit": short_hash, "pushed": pushed})
            except Exception as e:
                self._send_json({"ok": False, "error": str(e)}, 500)
            return

        if parsed.path == "/api/git-restore":
            ref = (payload.get("ref") or "").strip()
            if not ref:
                self._send_json({"ok": False, "error": "Missing ref"}, 400)
                return
            try:
                # Commit any dirty state first so nothing is ever lost
                subprocess.run(["git", "add", "-A"], cwd=ROOT)
                st = subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True).strip()
                if st:
                    subprocess.run(["git", "commit", "-m", "Auto-backup before restore"], cwd=ROOT)

                # Restore HTML files from target ref and re-run setup/sync if needed
                for rel in HTML_FILES + ["devin-tucker.vcf"]:
                    subprocess.run(["git", "checkout", ref, "--", rel], cwd=ROOT)

                # Ensure copy-editor.js and data-copy attributes stay present even if restored to claude-baseline
                setup_script = os.path.join(ROOT, "_ensure_copy_attrs.py")
                if os.path.exists(setup_script):
                    subprocess.run(["C:\\Python311\\python.exe", setup_script], cwd=ROOT)

                subprocess.run(["git", "add", "-A"], cwd=ROOT)
                st2 = subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT, text=True).strip()
                if st2:
                    subprocess.run(["git", "commit", "-m", f"Restore copy to {ref}"], cwd=ROOT)

                self._send_json({"ok": True})
            except Exception as e:
                self._send_json({"ok": False, "error": str(e)}, 500)
            return

        self._send_json({"ok": False, "error": "Not found"}, 404)


if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    server = http.server.ThreadingHTTPServer(("127.0.0.1", port), CopyServerHandler)
    print(f"Devin Tucker Site + Copy Studio running at http://localhost:{port}/")
    print(f"Copy Studio: http://localhost:{port}/copy-studio.html")
    server.serve_forever()

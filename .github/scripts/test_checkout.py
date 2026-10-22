#!/usr/bin/env python3
"""Read-only-remote smoke tests for the hosted sparse checkout benchmarks."""

import base64
import os
from pathlib import Path
import subprocess
import sys
import uuid


def git(*args, check=True):
    return subprocess.run(
        ["git", *args], check=check, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, text=True,
    )


def require(condition, message):
    if not condition:
        raise RuntimeError(message)
    print(f"PASS: {message}", flush=True)


def tracked_files():
    records = git("ls-tree", "-r", "-z", "HEAD", "--", "labels").stdout
    return {
        path: meta.split()[2]
        for record in records.split("\0") if record
        for meta, path in [record.split("\t", 1)]
    }


def check_metadata():
    files = tracked_files()
    metadata = {
        path: oid for path, oid in files.items()
        if Path(path).suffix in (".md", ".json")
    }
    require(bool(metadata), "tracked label metadata exists")
    for path, oid in metadata.items():
        require_file = Path(path)
        if not require_file.is_file() or git("hash-object", path).stdout.strip() != oid:
            raise RuntimeError(f"Missing or changed label metadata: {path}")
    require(True, f"all {len(metadata)} metadata files match Git, including OCR text")
    expected_ids = {Path(path).parts[1] for path in files
                    if len(Path(path).parts) > 2 and Path(path).parts[1].isdigit()}
    actual_ids = {path.name for path in Path("labels").iterdir()
                  if path.is_dir() and path.name.isdigit()}
    require(actual_ids == expected_ids, "all existing label ID directories remain available")
    unexpected = [
        str(path) for path in Path("labels").rglob("*")
        if path.is_file() and path.suffix not in (".md", ".json")
    ]
    require(not unexpected, f"archived images are absent: {unexpected[:3]}")
    require(not git("status", "--porcelain").stdout, "checkout is clean")
    return next(path for path in metadata if path.endswith("/README.md"))


def test_staging(readme):
    original = Path(readme).read_bytes()
    fixture = Path("labels") / f"checkout-smoke-{uuid.uuid4().hex}"
    fixture.mkdir()
    try:
        (fixture / "front_label.jpg").write_bytes(b"checkout smoke fixture, not a real image\n")
        (fixture / "README.md").write_text("Checkout smoke metadata\n")
        Path(readme).write_bytes(original + b"\nCheckout smoke OCR metadata update\n")
        git("add", "--sparse", "-A")
        changed = git("diff", "--cached", "--name-status").stdout.splitlines()
        expected = {
            f"M\t{readme}",
            f"A\t{fixture.as_posix()}/front_label.jpg",
            f"A\t{fixture.as_posix()}/README.md",
        }
        require(set(changed) == expected, "staging contains only fixture files and metadata update; no deletions")
    finally:
        git("reset", "--mixed", "HEAD")
        Path(readme).write_bytes(original)
        for path in fixture.iterdir():
            path.unlink()
        fixture.rmdir()
    require(not git("status", "--porcelain").stdout, "fixture cleanup leaves checkout clean")


def test_branches(profile, pr_number):
    branch = "automated/find-new-releases" if profile == "releases" else "automated/new-ttb-labels"
    remote_ref = f"refs/heads/{branch}"
    exists = git("ls-remote", "--exit-code", "--heads", "origin", remote_ref, check=False)
    if exists.returncode == 2:
        # PR refs are guaranteed to exist even when no production automation PR is open.
        remote_ref = f"refs/pull/{pr_number}/head"
        print(f"No {branch}; testing existing-ref path with {remote_ref}", flush=True)
    elif exists.returncode:
        raise RuntimeError(f"Cannot inspect automation branch: {exists.stderr}")
    git("fetch", "--depth=1", "--filter=blob:none", "--no-tags", "origin", remote_ref)
    expected_head = git("rev-parse", "FETCH_HEAD").stdout.strip()
    git("checkout", "-B", branch, "FETCH_HEAD")
    require(git("rev-parse", "HEAD").stdout.strip() == expected_head,
            "existing-ref fetch checks out FETCH_HEAD")
    require(git("branch", "--show-current").stdout.strip() == branch,
            "existing-ref checkout selects the automation branch locally")
    check_metadata()

    before = git("rev-parse", "HEAD").stdout.strip()
    missing = f"refs/heads/checkout-smoke-missing-{uuid.uuid4().hex}"
    absent = git("ls-remote", "--exit-code", "--heads", "origin", missing, check=False)
    require(absent.returncode == 2, "missing-ref case is genuinely absent, not a network/auth error")
    fetched = git("fetch", "--depth=1", "--filter=blob:none", "--no-tags",
                  "origin", missing, check=False)
    require(fetched.returncode != 0 and "couldn't find remote ref" in fetched.stderr.lower(),
            "missing branch fetch takes the expected fallback")
    require(git("rev-parse", "HEAD").stdout.strip() == before,
            "missing branch leaves the current checkout unchanged")


def main():
    profile, pr_number = sys.argv[1:]
    require(profile in ("build", "releases", "labels"), "known checkout profile")
    require(pr_number.isdigit(), "valid PR number")
    if profile == "build":
        require(not Path("labels").exists(), "build excludes the entire label archive")
        require(not git("status", "--porcelain").stdout, "build checkout is clean")
        return
    # Match checkout's temporary HTTP authentication without writing credentials to disk.
    token = os.environ.get("GH_TOKEN")
    if token:
        authorization = base64.b64encode(f"x-access-token:{token}".encode()).decode()
        os.environ.update(
            GIT_CONFIG_COUNT="1",
            GIT_CONFIG_KEY_0="http.https://github.com/.extraheader",
            GIT_CONFIG_VALUE_0=f"AUTHORIZATION: basic {authorization}",
        )
    test_staging(check_metadata())
    test_branches(profile, pr_number)
    test_staging(check_metadata())


if __name__ == "__main__":
    main()

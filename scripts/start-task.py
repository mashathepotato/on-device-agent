#!/usr/bin/env python3
"""Create an isolated task checkout using only Git and Python's standard library."""

import argparse
from pathlib import Path
import re
import subprocess
import sys


def git(*args, check=True):
    return subprocess.run(
        ["git", *args], check=check, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )


def slug(value):
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", value):
        raise argparse.ArgumentTypeError("use lowercase letters, digits, and single hyphens")
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("owner", type=slug)
    parser.add_argument("task", type=slug)
    parser.add_argument("--base", help="explicit base commit or branch (default: origin's default branch, or local main)")
    args = parser.parse_args()
    try:
        # Locate the main repository even when invoked from a linked worktree.
        common = Path(git("rev-parse", "--git-common-dir").stdout.strip()).resolve()
        if git("rev-parse", "--is-bare-repository").stdout.strip() == "true":
            parser.error("run this from a non-bare clone")
        root = common.parent
        branch = f"agent/{args.owner}/{args.task}"
        destination = root.parent / f"{root.name}-worktrees" / args.owner / args.task
        if destination.exists() or destination.is_symlink():
            parser.error(f"checkout already exists: {destination}")
        if git("show-ref", "--verify", "--quiet", f"refs/heads/{branch}", check=False).returncode == 0:
            parser.error(f"branch already exists: {branch}")

        remotes = git("remote").stdout.splitlines()
        if "origin" in remotes:
            git("fetch", "origin")
            if git("show-ref", "--verify", "--quiet", f"refs/remotes/origin/{branch}", check=False).returncode == 0:
                parser.error(f"task branch already exists on origin: {branch}")
        base = args.base
        if base is None:
            if "origin" in remotes:
                # Ask the server rather than trusting a stale local origin/HEAD.
                refs = git("ls-remote", "--symref", "origin", "HEAD").stdout
                match = re.search(r"^ref: refs/heads/(.+)\tHEAD$", refs, re.MULTILINE)
                if not match:
                    parser.error("cannot detect origin's default branch; use --base")
                base = f"refs/remotes/origin/{match.group(1)}"
            else:
                base = "refs/heads/main"
        commit = git("rev-parse", "--verify", "--end-of-options", f"{base}^{{commit}}").stdout.strip()
        git("worktree", "add", "-b", branch, str(destination), commit)
        print(f"Branch: {branch}\nCheckout: {destination}\n\nOpen this checkout in your harness and read AGENTS.md before editing.")
    except FileNotFoundError:
        print("Git is required but was not found on PATH.", file=sys.stderr)
        return 1
    except subprocess.CalledProcessError as error:
        print(error.stderr.strip() or str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

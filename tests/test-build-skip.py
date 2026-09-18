#!/usr/bin/env python3
"""Test: build cache (skip unchanged builds)

Unit test for the ls-remote based build cache that lets rpm-build-assist skip
the clone -> src.rpm -> chain sequence when nothing affecting the output has
changed. Does not require mock: it loads the script as a module and exercises
the cache methods against a throwaway local git repository.

Run directly, or via the test runner:
    ./run-tests test-build-skip.py
"""

import logging
import shutil
import subprocess
import sys
import tempfile
import types
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "rpm-build-assist"

fails = 0


def check(desc, expected, actual):
    global fails
    if expected == actual:
        print(f"  ok: {desc}")
    else:
        print(f"  FAIL: {desc} (expected {expected!r}, got {actual!r})")
        fails += 1


def load_assistant():
    """Load the extension-less script as a module and return a bare instance."""
    src = SCRIPT.read_text()
    mod = types.ModuleType("rba")
    mod.__file__ = str(SCRIPT)
    exec(compile(src, str(SCRIPT), "exec"), mod.__dict__)

    a = mod.MockBuildAssistant.__new__(mod.MockBuildAssistant)
    a.logger = logging.getLogger("test")
    a.mock_defines = []
    a.addrepo_urls = []
    a.force_rebuild = False
    # The result-cache index lives beside the config file.
    a.config_file = str(Path(tempfile.mkdtemp(prefix="rba-skip-cfg-")) /
                        "build-assist.yaml")
    a.localrepo_path = Path(tempfile.mkdtemp(prefix="rba-skip-lr-"))
    return a


def make_repo():
    """Create a throwaway git repo with one commit; return its path."""
    repo = tempfile.mkdtemp(prefix="rba-skip-repo-")

    def git(*args):
        subprocess.run(
            ["git", "-C", repo, "-c", "user.email=t@example.com",
             "-c", "user.name=test", *args],
            check=True, capture_output=True, text=True)

    git("init", "-q", "-b", "main")
    Path(repo, "file.txt").write_text("hello\n")
    git("add", "file.txt")
    git("commit", "-q", "-m", "initial")
    return repo, git


def make_result_dir(a, base, package):
    """Create a fake mock result directory and return the src.rpm path in it.

    The src.rpm file itself need not exist; _record_build only derives the NVR
    (and thus the result directory name) from the src.rpm's file name.
    """
    nvr = f"{package}-1.0-1.fc44"
    result_dir = a.localrepo_path / "results" / base / nvr
    result_dir.mkdir(parents=True, exist_ok=True)
    return str(result_dir / f"{nvr}.src.rpm"), result_dir


def main():
    a = load_assistant()
    repo, git = make_repo()
    cfg, pkg = "fedora-44-x86_64", "demo"
    src_rpm, result_dir = make_result_dir(a, cfg, pkg)

    commit = a._resolve_remote_commit(repo, "main")
    check("resolves branch to a 40-char commit", True, bool(commit) and len(commit) == 40)

    # Nothing recorded yet -> not current.
    check("not current before any build", False, a._build_is_current(cfg, pkg, commit))

    # Record a build -> now current, with a visible record and a symlink to it.
    a._record_build(cfg, pkg, commit, src_rpm)
    check("current after recording the build", True, a._build_is_current(cfg, pkg, commit))
    check("record file written in result dir", True,
          (result_dir / "build-assist.result").is_file())
    link = a._cache_link_path(pkg)
    check("result-cache entry is a symlink", True, link.is_symlink())
    check("symlink points into the result dir", True,
          link.resolve() == (result_dir / "build-assist.result").resolve())

    # Removing the result directory dangles the symlink -> not current.
    shutil.rmtree(result_dir)
    check("removing the result dir invalidates the cache", False,
          a._build_is_current(cfg, pkg, commit))

    # Rebuild the result dir and re-record, then remove the symlink itself.
    make_result_dir(a, cfg, pkg)
    a._record_build(cfg, pkg, commit, src_rpm)
    check("re-recording restores the match", True, a._build_is_current(cfg, pkg, commit))
    link.unlink()
    check("removing the symlink invalidates the cache", False,
          a._build_is_current(cfg, pkg, commit))

    # Re-record for the remaining key-comparison checks.
    a._record_build(cfg, pkg, commit, src_rpm)

    # Changing a macro invalidates the cache.
    a.mock_defines = ["--define=_foo bar"]
    check("macro change invalidates cache", False, a._build_is_current(cfg, pkg, commit))
    a.mock_defines = []
    check("reverting the macro restores the match", True, a._build_is_current(cfg, pkg, commit))

    # Changing an added repo invalidates the cache.
    a.addrepo_urls = ["https://example.invalid/repo"]
    check("addrepo change invalidates cache", False, a._build_is_current(cfg, pkg, commit))
    a.addrepo_urls = []

    # Build flags (with/without/define) participate in the cache key.
    a._record_build(cfg, pkg, commit, src_rpm, ["--with=py3"])
    check("current with matching build flags", True,
          a._build_is_current(cfg, pkg, commit, ["--with=py3"]))
    check("different build flags invalidate cache", False,
          a._build_is_current(cfg, pkg, commit, ["--without=py3"]))
    check("dropping build flags invalidates cache", False,
          a._build_is_current(cfg, pkg, commit))
    # Restore a flag-less record for the remaining checks.
    a._record_build(cfg, pkg, commit, src_rpm)

    # A different base config is a different build.
    check("different base config is not current", False,
          a._build_is_current("other", pkg, commit))

    # A new commit invalidates the cache.
    Path(repo, "file.txt").write_text("world\n")
    git("commit", "-qa", "-m", "second")
    commit2 = a._resolve_remote_commit(repo, "main")
    check("new commit produces a different SHA", True, commit2 != commit)
    check("new commit is not current", False, a._build_is_current(cfg, pkg, commit2))

    # --force bypasses the cache.
    a.force_rebuild = True
    check("force_rebuild bypasses the cache", False, a._build_is_current(cfg, pkg, commit))
    a.force_rebuild = False

    # Unresolvable ref -> no commit, never skip.
    check("unresolvable ref returns None", None, a._resolve_remote_commit(repo, "no-such-ref"))
    check("None commit is never current", False, a._build_is_current(cfg, pkg, None))
    # Recording a None commit writes nothing (no crash, stays not-current).
    ghost_src, _ = make_result_dir(a, cfg, "ghost")
    a._record_build(cfg, "ghost", None, ghost_src)
    check("recording a None commit does not make it current",
          False, a._build_is_current(cfg, "ghost", None))

    print()
    if fails:
        print("build-cache check(s) failed.")
        return 1
    print("All build-cache checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

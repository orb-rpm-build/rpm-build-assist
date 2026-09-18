#!/usr/bin/env python3
"""Test: per-source build flags (with/without/define)

Unit test for translating a build source's with/without/define fields into
mock arguments. Does not require mock: it loads the script as a module and
calls _parse_build_flags directly.

Run directly, or via the test runner:
    ./run-tests test-build-flags.py
"""

import logging
import sys
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
    return a


def main():
    a = load_assistant()

    # No fields -> no flags.
    check("empty source yields no flags", [], a._parse_build_flags({}))

    # Scalars.
    check("with scalar", ["--with=python"],
          a._parse_build_flags({"with": "python"}))
    check("without scalar", ["--without=tests"],
          a._parse_build_flags({"without": "tests"}))
    check("define scalar", ["--define=debug 1"],
          a._parse_build_flags({"define": "debug 1"}))

    # Lists.
    check("with list", ["--with=a", "--with=b"],
          a._parse_build_flags({"with": ["a", "b"]}))
    check("without list", ["--without=x", "--without=y"],
          a._parse_build_flags({"without": ["x", "y"]}))
    check("define list", ["--define=m 1", "--define=n 2"],
          a._parse_build_flags({"define": ["m 1", "n 2"]}))

    # Combination, in with/without/define order.
    check("combined fields keep with/without/define order",
          ["--with=docs", "--without=tests", "--define=debug 1"],
          a._parse_build_flags({"without": "tests", "define": "debug 1",
                                "with": "docs"}))

    # Unrelated keys (type/url/packages) are ignored.
    check("unrelated keys ignored", ["--with=foo"],
          a._parse_build_flags({"type": "dist-git", "url": "u",
                                "packages": ["p"], "with": "foo"}))

    # An invalid type is a fatal configuration error.
    try:
        a._parse_build_flags({"with": {"not": "allowed"}})
        check("invalid flag type exits", "SystemExit", "no exit")
    except SystemExit:
        check("invalid flag type exits", "SystemExit", "SystemExit")

    print()
    if fails:
        print("build-flags check(s) failed.")
        return 1
    print("All build-flags checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

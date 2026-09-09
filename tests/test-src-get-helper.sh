#!/bin/bash
# Test: rpm-build-assist-src-get helper behavior
#
# Unit test for the src-get helper that mock's SCM plugin runs as
# distgit_src_get. It does not require mock; it stubs spectool on PATH so the
# helper's own logic (invoke spectool, run *sources.sh, propagate failures) can
# be verified deterministically.
#
# Run directly, or via the test runner:
#   ./run-tests test-src-get-helper.sh
set -u

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HELPER="$SCRIPT_DIR/../rpm-build-assist-src-get"

fails=0
check() {
    # check DESCRIPTION EXPECTED ACTUAL
    if [ "$2" = "$3" ]; then
        echo "  ok: $1"
    else
        echo "  FAIL: $1 (expected '$2', got '$3')"
        fails=$((fails + 1))
    fi
}

# Build a throwaway workspace with a stub spectool on PATH.
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

BIN="$WORK/bin"
mkdir -p "$BIN"
# Stub spectool: records that it was called (and its args), exit status is
# controlled by the SPECTOOL_EXIT env var so we can test tolerance of failures.
cat > "$BIN/spectool" <<'EOF'
#!/bin/sh
echo "$@" >> "$SPECTOOL_CALLS"
exit "${SPECTOOL_EXIT:-0}"
EOF
chmod +x "$BIN/spectool"
# Stub rpmautospec: records its args and, on success, "processes" the spec by
# writing the target file with a recognizable marker so we can tell the helper
# swapped it in. Exit status is controlled by RPMAUTOSPEC_EXIT.
cat > "$BIN/rpmautospec" <<'EOF'
#!/bin/sh
echo "$@" >> "$RPMAUTOSPEC_CALLS"
# args: process-distgit SRC TARGET
if [ "${RPMAUTOSPEC_EXIT:-0}" -eq 0 ]; then
    echo "processed-by-rpmautospec" > "$3"
fi
exit "${RPMAUTOSPEC_EXIT:-0}"
EOF
chmod +x "$BIN/rpmautospec"
export PATH="$BIN:$PATH"

# --- Case 1: runs spectool and a sources.sh, succeeds ---
run_case() {
    # Creates a fresh checkout dir; caller populates it, then we run the helper.
    CO="$WORK/co"
    rm -rf "$CO"; mkdir -p "$CO"
    export SPECTOOL_CALLS="$WORK/spectool-calls"
    : > "$SPECTOOL_CALLS"
    export RPMAUTOSPEC_CALLS="$WORK/rpmautospec-calls"
    : > "$RPMAUTOSPEC_CALLS"
    export RPMAUTOSPEC_EXIT=0
}

run_case
: > "$CO/foo.spec"
cat > "$CO/gen-sources.sh" <<'EOF'
#!/bin/sh
touch generated.tar.gz
EOF
export SPECTOOL_EXIT=0
( cd "$CO" && "$HELPER" foo.spec ) >/dev/null 2>&1
check "sources.sh executed (marker created)" "yes" "$([ -e "$CO/generated.tar.gz" ] && echo yes || echo no)"
check "spectool invoked with spec" "-g foo.spec" "$(cat "$SPECTOOL_CALLS")"
( cd "$CO" && "$HELPER" foo.spec ) >/dev/null 2>&1
check "exit 0 on success" "0" "$?"

# --- Case 2: no sources.sh present -> still succeeds, still calls spectool ---
run_case
: > "$CO/foo.spec"
export SPECTOOL_EXIT=0
( cd "$CO" && "$HELPER" foo.spec ) >/dev/null 2>&1
check "exit 0 when no sources.sh" "0" "$?"
check "spectool still invoked" "-g foo.spec" "$(cat "$SPECTOOL_CALLS")"

# --- Case 3: spectool failure is tolerated ---
run_case
: > "$CO/foo.spec"
cat > "$CO/gen-sources.sh" <<'EOF'
#!/bin/sh
touch generated.tar.gz
EOF
export SPECTOOL_EXIT=1
( cd "$CO" && "$HELPER" foo.spec ) >/dev/null 2>&1
rc=$?
check "spectool failure does not abort helper" "0" "$rc"
check "sources.sh still ran after spectool failure" "yes" "$([ -e "$CO/generated.tar.gz" ] && echo yes || echo no)"

# --- Case 4: sources.sh failure is ignored ---
# Source-assembly scripts have unreliable exit status (e.g. failing to upload
# to a lookaside cache when offline), so a non-zero exit is not treated as
# fatal; a genuinely missing source fails later during src.rpm assembly.
run_case
: > "$CO/foo.spec"
cat > "$CO/gen-sources.sh" <<'EOF'
#!/bin/sh
touch generated.tar.gz
exit 3
EOF
export SPECTOOL_EXIT=0
( cd "$CO" && "$HELPER" foo.spec ) >/dev/null 2>&1
check "sources.sh failure does not abort helper" "0" "$?"
check "sources.sh still ran despite failing exit" "yes" "$([ -e "$CO/generated.tar.gz" ] && echo yes || echo no)"

# --- Case 5: missing spec argument -> usage error ---
export SPECTOOL_EXIT=0
"$HELPER" >/dev/null 2>&1
check "missing spec argument exits non-zero" "yes" "$([ $? -ne 0 ] && echo yes || echo no)"

# --- Case 6: multiple *sources.sh scripts all run ---
run_case
: > "$CO/foo.spec"
printf '#!/bin/sh\ntouch a.done\n' > "$CO/a-sources.sh"
printf '#!/bin/sh\ntouch b.done\n' > "$CO/b-sources.sh"
export SPECTOOL_EXIT=0
( cd "$CO" && "$HELPER" foo.spec ) >/dev/null 2>&1
check "first *sources.sh ran" "yes" "$([ -e "$CO/a.done" ] && echo yes || echo no)"
check "second *sources.sh ran" "yes" "$([ -e "$CO/b.done" ] && echo yes || echo no)"

# --- Case 7: a spec using %autorelease is processed by rpmautospec ---
run_case
printf 'Release: %%autorelease\n%%changelog\n%%autochangelog\n' > "$CO/foo.spec"
( cd "$CO" && "$HELPER" foo.spec ) >/dev/null 2>&1
check "rpmautospec invoked for autospec spec" "process-distgit foo.spec foo.spec.rpmautospec" "$(cat "$RPMAUTOSPEC_CALLS")"
check "processed spec swapped in" "processed-by-rpmautospec" "$(cat "$CO/foo.spec")"
check "no leftover temp spec" "no" "$([ -e "$CO/foo.spec.rpmautospec" ] && echo yes || echo no)"

# --- Case 8: a spec without rpmautospec macros is left untouched ---
run_case
printf 'Release: 1%%{?dist}\n' > "$CO/foo.spec"
( cd "$CO" && "$HELPER" foo.spec ) >/dev/null 2>&1
check "rpmautospec not invoked without macros" "" "$(cat "$RPMAUTOSPEC_CALLS")"
check "non-autospec spec unchanged" "Release: 1%{?dist}" "$(cat "$CO/foo.spec")"

# --- Case 9: rpmautospec failure is tolerated, spec left intact ---
run_case
printf 'Release: %%autorelease\n' > "$CO/foo.spec"
export RPMAUTOSPEC_EXIT=1
( cd "$CO" && "$HELPER" foo.spec ) >/dev/null 2>&1
check "rpmautospec failure does not abort helper" "0" "$?"
check "spec unchanged after rpmautospec failure" "Release: %autorelease" "$(cat "$CO/foo.spec")"
check "no leftover temp spec after failure" "no" "$([ -e "$CO/foo.spec.rpmautospec" ] && echo yes || echo no)"

# --- Case 10: rpmautospec absent -> warn and continue, spec left intact ---
# Run with a PATH that provides the helper's coreutils but no rpmautospec.
NOAUTO="$WORK/noauto"
rm -rf "$NOAUTO"; mkdir -p "$NOAUTO"
for tool in grep mv rm basename cat sh; do
    ln -sf "$(command -v "$tool")" "$NOAUTO/$tool"
done
cp "$BIN/spectool" "$NOAUTO/spectool"
run_case
printf 'Release: %%autorelease\n' > "$CO/foo.spec"
( cd "$CO" && PATH="$NOAUTO" "$HELPER" foo.spec ) >/dev/null 2>&1
check "helper exits 0 when rpmautospec is absent" "0" "$?"
check "spec unchanged when rpmautospec is absent" "Release: %autorelease" "$(cat "$CO/foo.spec")"

echo
if [ "$fails" -eq 0 ]; then
    echo "All src-get helper checks passed."
    exit 0
else
    echo "$fails src-get helper check(s) failed."
    exit 1
fi

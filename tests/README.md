# rpm-build-assist Tests

This directory contains test configurations for rpm-build-assist.

## Running Tests

Run all tests:
```bash
./run-tests
```

Run specific tests:
```bash
./run-tests test-self-build-rpm.yaml
```

Run with verbose output:
```bash
./run-tests -v
```

Keep build artifacts after testing:
```bash
./run-tests -k
```

List available tests:
```bash
./run-tests --list
```

## Test Structure

Tests are YAML configuration files with a `test-` prefix. Each test:

1. Defines a complete rpm-build-assist configuration
2. Is executed by the test runner
3. Must complete successfully (exit code 0) to pass
4. Validates specific functionality

## Current Tests

### test-self-build-rpm.yaml

Validates basic RPM building from git:
- Building from git SCM type
- Standard installation type
- Ensures rpm-build-assist can build itself

### test-self-build-container.yaml

Validates container image building:
- Building from git SCM type
- Container installation type
- Container image generation and tagging

### test-src-get-helper.sh

Unit test for the `rpm-build-assist-src-get` helper (run by mock's SCM plugin
as `distgit_src_get`). Unlike the `.yaml` tests, unit tests (`.sh` or `.py`)
are run directly by the test runner and do **not** require mock. This one stubs
`spectool` and `rpmautospec` on `PATH` to verify the helper expands
`%autorelease`/`%autochangelog`, fetches online sources, runs any
source-assembly script, and tolerates missing tools and non-fatal exit codes.

### test-build-skip.py

Unit test for the build cache that skips unchanged builds. It loads the script
as a module and exercises the `git ls-remote` commit resolution and the
result-cache symlink logic (recording a build, and invalidation by removing
either the symlink or the result directory) against a throwaway local git
repository (no mock required).

## Writing New Tests

Create a new YAML file in this directory with `test-` prefix:

```yaml
# Test: Brief description
#
# Details about what this test validates

base: fedora-44-x86_64

build:
  - type: git
    url: {{REPO_BASE_URL}}
    packages:
      - package-name:branch

install:
  type: standard
```

Name the file descriptively: `test-{feature}-{scenario}.yaml`

### Template Variables

Test files support template variables that are substituted at runtime:

- `{{REPO_BASE_URL}}` - The parent directory of the working directory as a file:// URL
  - Example: `file:///home/user/git/orb-project/`
  - Use this to test the working directory code instead of remote repositories

### Test Guidelines

- **One feature per test** - Keep tests focused
- **Self-contained** - Don't depend on other tests
- **Fast** - Prefer simple packages when possible
- **Document** - Add comments explaining what's being tested
- **No localrepo** - Test runner provides this automatically
- **Use templates** - Use `{{REPO_BASE_URL}}` to test the working directory

## Environment Variables

- `SKIP_MOCK_TESTS` - Skip tests that require mock (for CI)
- `TEST_LOCALREPO` - Override test localrepo path (default: `./test-localrepo`)

## CI Integration

For continuous integration:

```bash
# Skip mock tests if mock not available
SKIP_MOCK_TESTS=1 ./run-tests

# Or run with mock in container
podman run --rm --privileged \
  -v $PWD:/workspace:Z \
  -w /workspace \
  fedora:40 \
  bash -c "dnf install -y mock python3-pyyaml && ./run-tests"
```

## Test Artifacts

Test artifacts are stored in `test-localrepo/{test-name}/`:
- Built RPMs
- Mock logs
- Repository metadata

Artifacts are cleaned up automatically after successful tests unless `--keep` is specified.

## Troubleshooting

### Permission denied (mock)

Ensure you're in the mock group:
```bash
sudo usermod -a -G mock $USER
# Log out and back in
```

### Test fails but manual run succeeds

Check that the test doesn't depend on your local environment. Tests should be self-contained.

### All tests skipped

Either `SKIP_MOCK_TESTS` is set or tests aren't found. Check:
```bash
ls tests/test-*.yaml
```

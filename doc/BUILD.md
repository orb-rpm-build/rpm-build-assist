# Building Documentation

## Quick Start (Container-based, Recommended)

Build the documentation using podman or docker (auto-detected):

```bash
./build-docs
```

View the built documentation:

```bash
# Open in browser (Linux)
xdg-open doc/build/html/index.html

# Or serve locally
cd doc/build/html
python3 -m http.server 8000
# Visit http://localhost:8000
```

## Manual Build (Without Containers)

If you prefer to build locally without containers:

### Prerequisites
```bash
# Install Python dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r doc/requirements.txt
```

### Build HTML
```bash
cd doc
sphinx-build -b html source build/html
```

### Serve locally
```bash
cd doc/build/html
python3 -m http.server 8000
```

Then open http://localhost:8000

## Using Make (if available)

If you have `make` installed:

```bash
cd doc
make html
make serve
```

## Output Location

Built documentation is in: `doc/build/html/`

Open `doc/build/html/index.html` in your browser.

## Clean Build

To remove previous build artifacts:

```bash
rm -rf doc/build/
```

Then rebuild.

## Troubleshooting

### Container build fails
- Ensure podman or docker is installed and running
- Check that you have permission to run containers
- Try with sudo if needed (for docker)

### Permission errors
The script uses `:Z` flag for SELinux systems. If you're not on SELinux and get errors, edit `build-docs` and remove `:Z` from the volume mount.

### Documentation not updating
Clean the build directory and rebuild:
```bash
rm -rf doc/build/
./build-docs
```

## CI/CD Build

See `.github/workflows/docs.yml` for GitHub Actions example.
See `.gitlab-ci.yml` for GitLab CI example.
See `.readthedocs.yaml` for Read the Docs configuration.

## Publishing

See [PUBLISHING.md](PUBLISHING.md) for detailed instructions on publishing the documentation to various platforms.

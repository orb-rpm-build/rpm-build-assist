# Documentation Quick Reference

This project includes comprehensive Sphinx documentation.

## Quick Start

**Build the documentation:**

```bash
./build-docs
```

This builds the docs in a container (uses podman or docker automatically).

**View the documentation:**

```bash
# Open directly in browser
xdg-open doc/build/html/index.html

# Or serve with Python
cd doc/build/html && python3 -m http.server 8000
# Then visit http://localhost:8000
```

## What's Included

The documentation covers:

- **User Guide**: Installation, usage, getting started
- **Tutorials**: Step-by-step guides for common tasks
  - First build
  - Container builds
  - Software collections
- **Format Reference**: Complete YAML configuration reference
- **How-To Guides**: 
  - Building from mixed sources
  - Using persistent repositories
  - Custom macros
  - Troubleshooting
- **Reference**: Command-line options, install types, SCM types

## Documentation Files

```
doc/
├── source/
│   ├── index.rst                    # Documentation home
│   ├── main_about.rst               # About the project
│   ├── main_install.rst             # Installation guide
│   ├── main_using.rst               # Usage guide
│   ├── tutorial/                    # Tutorials
│   │   ├── first_build.rst
│   │   ├── container_builds.rst
│   │   └── software_collections.rst
│   ├── format/                      # Format reference
│   │   ├── yaml_format.rst
│   │   ├── build_section.rst
│   │   ├── install_section.rst
│   │   └── variables.rst
│   ├── reference/                   # Reference docs
│   │   ├── command_line.rst
│   │   ├── install_types.rst
│   │   └── scm_types.rst
│   └── howto/                       # How-to guides
│       ├── mixed_sources.rst
│       ├── persistent_repos.rst
│       ├── custom_macros.rst
│       └── troubleshooting.rst
├── BUILD.md                         # Build instructions
├── PUBLISHING.md                    # Publishing guide
└── README.md                        # Doc overview
```

## Publishing

The documentation is ready to publish to:

- **Read the Docs** (recommended) - See [doc/PUBLISHING.md](doc/PUBLISHING.md)
- **GitHub Pages** - Automated with GitHub Actions
- **GitLab Pages** - Automated with GitLab CI
- **Self-hosted** - Using the provided Dockerfile

Configuration files are included:
- `.readthedocs.yaml` - Read the Docs config
- `Dockerfile.docs` - Docker build
- `doc/docker-compose.yml` - Docker Compose setup

See [doc/PUBLISHING.md](doc/PUBLISHING.md) for complete publishing instructions.

## Local Development

If you want to edit the documentation and see changes live:

1. Build once: `./build-docs.sh`
2. Edit `.rst` files in `doc/source/`
3. Rebuild: `./build-docs.sh`
4. Refresh browser

## More Information

- [doc/BUILD.md](doc/BUILD.md) - Detailed build instructions
- [doc/PUBLISHING.md](doc/PUBLISHING.md) - Publishing guide
- [doc/README.md](doc/README.md) - Documentation overview

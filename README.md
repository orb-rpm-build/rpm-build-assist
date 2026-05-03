# rpm-build-assist

A Python tool to build RPM packages using mock with SCM (Source Code Management) integration. This tool simplifies building multiple related packages from source control repositories and optionally installing them into various targets like containers, flatpaks, or software collections.

## Features

- Build multiple RPM packages from Git repositories using mock
- Support for dist-git, git, and other SCM methods
- Automatic macro configuration for flatpak and software collection builds
- Container image creation with built packages installed
- Local repository management with support for both temporary and persistent repositories
- Dependency resolution across builds using mock's chain mode
- Verbose logging support for debugging
- YAML-based configuration for easy management
- Automatic detection of podman or docker for container builds

## Requirements

- Python 3.6 or later
- mock (RPM building tool)
- PyYAML library
- Appropriate permissions to run mock (typically membership in the `mock` group)
- podman or docker (optional, required for container install type)

### Installation

```bash
# Install dependencies
sudo dnf install mock python3-pyyaml

# Add yourself to the mock group (then log out and back in)
sudo usermod -a -G mock $USER

# Make the script executable
chmod +x rpm-build-assist
```

## Usage

```bash
# Use default configuration file (build-assist.yaml)
./rpm-build-assist

# Specify a custom configuration file
./rpm-build-assist -c my-config.yaml

# Enable verbose output
./rpm-build-assist -v

# Use a persistent local repository
./rpm-build-assist --localrepo /path/to/repo

# Combine options
./rpm-build-assist --verbose --config custom.yaml --localrepo ~/rpm-builds/localrepo
```

### Command-line Arguments

- `-c`, `--config FILE`: Path to YAML configuration file (default: `build-assist.yaml`)
- `-v`, `--verbose`: Enable verbose output for detailed logging
- `--localrepo PATH`: Path to local repository directory (default: create temporary directory)

## Configuration File Format

The configuration file is a YAML document with up to three top-level elements:

### 1. base (required)

A string identifying the mock configuration to use for builds.

```yaml
base: fedora-39-x86_64
```

### 2. build (required)

A list of source repositories and packages to build. Each entry contains:

- **type** (optional): SCM method to use (default: `dist-git`)
  - Supported: `dist-git`, `git`, `svn`, `cvs`
- **url** (required): Base URL for the repositories
- **packages** (required): List of packages to build
  - Format: `package-name:branch`
  - If no branch is specified, `main` is used

```yaml
build:
  - type: dist-git
    url: https://src.fedoraproject.org/rpms/
    packages:
      - htop:rawhide
      - vim:f39
      - emacs

  - type: git
    url: https://github.com/myorg/
    packages:
      - myapp:main
      - mylib:v1.0
```

### 3. install (optional)

Defines how built packages will be installed. This section affects the build process by setting appropriate RPM macros.

- **type** (required): Installation target type
  - `flatpak`: Builds for flatpak (uses `/app` prefix)
  - `software-collection`: Builds for software collection (uses `/opt/{collection}` prefix)
  - `package-collection`: Builds for package collection with rpath (uses `/opt/{collection}` prefix with $ORIGIN-based library discovery)
  - `container`: Container image installation (creates container image with packages installed)
  - `install-media`: Installation media creation (not yet implemented)
  - `live-usb`: Live USB image creation (not yet implemented)
- **collection** (required for software-collection and package-collection): Name of the collection
- **base_image** (required for container): Base container image to start from
- **tag** (required for container): Tag for the resulting container image
- **registry** (optional for container): Registry to push the image to
- **packages** (required): List of package names to install

```yaml
install:
  type: flatpak
  packages:
    - myapp
    - mylib
```

## Examples

### Example 1: Basic Build

Build packages from Fedora dist-git:

```yaml
base: fedora-39-x86_64

build:
  - type: dist-git
    url: https://src.fedoraproject.org/rpms/
    packages:
      - htop:rawhide
      - tmux:f39
      - neovim:rawhide
```

### Example 2: Flatpak Build

Build packages configured for flatpak installation:

```yaml
base: fedora-39-x86_64

build:
  - type: git
    url: https://github.com/myorg/
    packages:
      - myapp:main
      - myapp-plugins:main

install:
  type: flatpak
  packages:
    - myapp
    - myapp-plugins
```

This automatically configures the build to use `/app` as the prefix instead of `/usr`.

### Example 3: Software Collection

Build a software collection with custom prefix:

```yaml
base: fedora-39-x86_64

build:
  - type: git
    url: https://internal.example.com/git/
    packages:
      - python311:main
      - python311-pip:main
      - python311-setuptools:main

install:
  type: software-collection
  collection: python311
  packages:
    - python311
    - python311-pip
    - python311-setuptools
```

This configures the build to use `/opt/python311` as the prefix.

### Example 4: Container Image Build

Build packages and create a container image:

```yaml
base: fedora-39-x86_64

build:
  - type: dist-git
    url: https://src.fedoraproject.org/rpms/
    packages:
      - nginx:rawhide
      - postgresql:f39

  - type: git
    url: https://github.com/company/
    packages:
      - webapp:v2.0

install:
  type: container
  base_image: registry.fedoraproject.org/fedora:39
  tag: company/webapp:v2.0
  registry: quay.io/company  # Optional: push to registry
  packages:
    - nginx
    - postgresql
    - webapp
```

This builds all packages, then creates a container image with them installed. The image:
- Starts from `registry.fedoraproject.org/fedora:39`
- Installs nginx, postgresql, and webapp from the local repository
- Is tagged as `company/webapp:v2.0`
- Is pushed to `quay.io/company/webapp:v2.0` (if registry is specified)

### Example 5: Mixed Sources

Build from multiple repository sources:

```yaml
base: fedora-39-x86_64

build:
  # Official Fedora packages
  - type: dist-git
    url: https://src.fedoraproject.org/rpms/
    packages:
      - nginx:rawhide
      - postgresql:f39

  # Custom packages from GitHub
  - type: git
    url: https://github.com/company/
    packages:
      - webapp:v2.0
      - webapp-utils:v2.0

  # Internal packages
  - type: git
    url: https://git.internal.example.com/
    packages:
      - company-theme:main
      - company-branding:release

install:
  type: container
  packages:
    - nginx
    - postgresql
    - webapp
    - company-theme
```

## How It Works

1. **Configuration Loading**: Reads and validates the YAML configuration file

2. **Install Section Processing**: If an install section is present, processes it first to determine if special RPM macros need to be defined (e.g., for flatpak or software collections)

3. **Local Repository Setup**: Sets up a local repository directory to store all built RPMs, allowing packages to depend on each other
   - Uses `--localrepo` CLI option if specified
   - Otherwise uses `localrepo` from YAML config if specified
   - Otherwise creates a temporary directory (default behavior)
   - Creates the directory if it doesn't exist

4. **Package Building**: For each package:
   - Constructs the full repository URL
   - Invokes mock with appropriate SCM options
   - Uses `--chain` to enable dependency resolution from the local repository
   - Stores built RPMs in the local repository

5. **Installation**: Processes the install section to install packages:
   - For `container` type: Creates a Containerfile, builds image with packages, optionally pushes to registry
   - For other types: Implementation depends on install type

## Mock Integration

The tool uses mock's SCM plugin to:

- Clone repositories from source control
- Check out specific branches
- Automatically create source tarballs
- Build RPMs in a clean chroot environment

Key mock options used:

- `--scm-enable`: Enable SCM support
- `--scm-option method=<type>`: Specify SCM method
- `--scm-option package=<name>`: Package name
- `--scm-option branch=<branch>`: Branch to check out
- `--scm-option spec=<file>`: Spec file to use
- `--scm-option write_tar=True`: Auto-create source tarball
- `--localrepo=<path>`: Local repository for built packages
- `--chain`: Enable chained builds with dependency resolution

## RPM Macro Customization

For special installation types, the tool automatically configures RPM macros:

### Flatpak

All standard paths are prefixed with `/app`:

- `_prefix` → `/app`
- `_bindir` → `/app/bin`
- `_libdir` → `/app/lib`
- `_datadir` → `/app/share`
- etc.

### Software Collections

All standard paths are prefixed with `/opt/{collection}`:

- `_prefix` → `/opt/{collection}`
- `_bindir` → `/opt/{collection}/bin`
- `_libdir` → `/opt/{collection}/lib`
- `_datadir` → `/opt/{collection}/share`
- etc.

## Logging

The tool uses Python's logging module with two verbosity levels:

- **Normal mode**: Shows INFO level messages (major steps and results)
- **Verbose mode** (`-v`): Shows DEBUG level messages (detailed command execution and configuration)

## Container Install Type

The `container` install type builds a container image with your custom RPM packages installed. This is useful for:

- Creating deployment-ready application containers
- Testing packages in an isolated environment
- Building container images with custom package versions
- Distributing applications via container registries

### How It Works

1. Builds all specified RPM packages using mock
2. Creates a temporary build context directory
3. Copies the local RPM repository to the build context
4. Generates a Containerfile that:
   - Starts from the specified base image
   - Sets up a DNF repository pointing to the local RPMs
   - Installs the specified packages
   - Cleans the DNF cache to minimize image size
5. Builds the container image using podman or docker
6. Optionally pushes the image to a registry

### Container Configuration

Required fields:
- `base_image`: Base container image (e.g., `registry.fedoraproject.org/fedora:39`)
- `tag`: Tag for the resulting image (e.g., `myapp:latest`)
- `packages`: List of package names to install

Optional fields:
- `registry`: Registry to push to (e.g., `quay.io/myorg`)

### Registry Authentication

If pushing to a registry, authenticate first:

```bash
# For podman
podman login quay.io

# For docker
docker login quay.io
```

## Troubleshooting

### Permission Denied Errors

Make sure you're a member of the `mock` group:

```bash
sudo usermod -a -G mock $USER
# Log out and back in for changes to take effect
```

### Build Failures

Run with verbose mode to see detailed mock output:

```bash
./rpm-build-assist -v
```

Check mock logs in `/var/lib/mock/<config>/result/` for specific build errors.

### Missing Dependencies

Ensure all required tools are installed:

```bash
sudo dnf install mock python3-pyyaml git

# For container builds, also install:
sudo dnf install podman  # or docker
```

### Container Build Issues

**Error: "Neither podman nor docker found"**
- Install podman: `sudo dnf install podman`
- Or install docker: `sudo dnf install docker`

**Error: "Failed to push container image"**
- Ensure you're logged in: `podman login <registry>`
- Check that the tag format is correct
- Verify network connectivity to the registry

**Image not found after build**
- Check image exists: `podman images`
- Verify the tag matches what was specified in config
- Check for build errors in verbose output

## License

This tool is provided as-is for use in building RPM packages with mock.

## Contributing

Contributions are welcome! Please ensure any changes maintain compatibility with the YAML configuration format and mock's SCM plugin.

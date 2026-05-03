# rpm-build-assist

## What is rpm-build-assist?

`rpm-build-assist` is a tool for orchestrating RPM package builds from source control repositories using mock. It allows you to define entire build pipelines in a single YAML file, automatically managing dependencies, local repositories, and installation targets like containers and software collections.

## Why should I use rpm-build-assist?

**Declarative build definitions**
  Define all your builds in a single YAML configuration file. Specify what to build, from where, and how to package it - rpm-build-assist handles the orchestration.

**Dependency resolution**
  Packages are built in order with automatic dependency resolution. Later packages can depend on earlier ones through a managed local repository.

**Multiple source support**
  Build from Fedora dist-git, GitHub, GitLab, or any git/svn/cvs repository. Mix and match sources in a single build pipeline.

**Flexible packaging**
  Create standard RPMs, flatpak packages, software collections, package collections with RPATH, or container images - all from the same build configuration.

**CI/CD friendly**
  Simple command-line interface and declarative configuration make integration with CI/CD pipelines straightforward.

## How does rpm-build-assist work?

rpm-build-assist operates on a YAML configuration file describing your build pipeline:

1. Reads your configuration defining sources and packages
2. Sets up a local RPM repository for dependency resolution
3. Builds each package in order using mock's SCM plugin
4. Stores built RPMs in the local repository
5. Optionally creates installation targets (containers, etc.)

## Quick example

Create a `build-assist.yaml`:

```yaml
base: fedora-39-x86_64

build:
  - type: dist-git
    url: https://src.fedoraproject.org/rpms/
    packages:
      - nginx:rawhide

  - type: git
    url: https://github.com/myorg/
    packages:
      - webapp:v2.0

install:
  type: container
  base_image: registry.fedoraproject.org/fedora:39
  tag: myapp:latest
  packages:
    - nginx
    - webapp
```

Run the build:

```bash
./rpm-build-assist -v
```

This builds nginx from Fedora and your webapp from GitHub, then creates a container image with both installed.

## How can I get started?

First, install the requirements:

```bash
sudo dnf install mock python3-pyyaml
sudo usermod -a -G mock $USER
# Log out and back in
```

Then follow the [First Build Tutorial](doc/source/tutorial/first_build.rst) to create your first build, or explore the comprehensive documentation:

**Documentation**
- [Installation Guide](doc/source/main_install.rst)
- [User Guide](doc/source/main_using.rst)
- [Tutorials](doc/source/tutorial/first_build.rst) - First build, containers, software collections
- [Format Reference](doc/source/format/yaml_format.rst) - Complete YAML configuration reference
- [How-To Guides](doc/source/howto/mixed_sources.rst) - Common tasks and troubleshooting

**Build the documentation locally:**

```bash
./build-docs
xdg-open doc/build/html/index.html
```

**Examples**

See the [examples/](examples/) directory for sample configurations demonstrating various features.

## Features

- Build multiple RPM packages from source control in a single run
- Support for dist-git, git, svn, and cvs repositories
- Automatic dependency resolution using mock's chain mode
- Local repository management (temporary or persistent)
- Automatic RPM macro configuration for special installation types
- Container image creation with built packages installed
- Flatpak and software collection support
- Package collections with automatic RPATH configuration
- Additional repository support for build-time dependencies
- Verbose logging for debugging

## License

This tool is provided as-is for use in building RPM packages with mock.

## Contributing

Contributions are welcome! Please ensure any changes maintain compatibility with the YAML configuration format and mock's SCM plugin.

Report issues on Codeberg: https://codeberg.org/orb-project/rpm-build-assist/issues

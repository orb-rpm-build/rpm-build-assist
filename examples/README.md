# rpm-build-assist Examples

This directory contains example configuration files demonstrating various features.

## Quick Start

Copy an example and customize it:

```bash
cp examples/build-assist.yaml.example build-assist.yaml
# Edit build-assist.yaml for your needs
./rpm-build-assist -v
```

## Examples

### build-assist.yaml.example

Comprehensive example showing all major features:
- Building from dist-git and git repositories
- Using persistent package repositories
- Adding custom repository URLs
- Flatpak builds
- Software collections
- Container image builds

Uncomment and modify the sections you need.

## Additional Examples

For working examples that are tested as part of the project, see the `tests/` directory:
- `tests/test-self-build-rpm.yaml` - Building rpm-build-assist as an RPM
- `tests/test-self-build-container.yaml` - Building as a container image

These test configurations serve as validated, working examples.

## More Examples

For additional examples and tutorials, see the documentation:

- **[First Build Tutorial](../doc/source/tutorial/first_build.rst)** - Simple single package
- **[Container Builds](../doc/source/tutorial/container_builds.rst)** - Building container images
- **[Software Collections](../doc/source/tutorial/software_collections.rst)** - SCLs and package collections
- **[Mixed Sources](../doc/source/howto/mixed_sources.rst)** - Multiple repositories

## Creating Your Own Configuration

Basic structure:

```yaml
base: fedora-39-x86_64

build:
  - type: dist-git  # or: git, svn, cvs
    url: https://src.fedoraproject.org/rpms/
    packages:
      - package-name:branch

install:  # Optional
  type: container  # or: flatpak, software-collection, package-collection
  # type-specific fields...
  packages:
    - package-name
```

See the [YAML format reference](../doc/source/format/yaml_format.rst) for complete documentation.

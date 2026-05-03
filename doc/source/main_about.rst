About rpm-build-assist
======================

What is rpm-build-assist?
--------------------------

``rpm-build-assist`` is a powerful tool for orchestrating RPM package builds
from source control repositories. It provides a YAML-based declarative
interface for defining complex build pipelines involving multiple packages
from various sources.

Key capabilities
----------------

* **Declarative build definitions**: Define your entire build pipeline in a
  single YAML configuration file
* **Multiple source support**: Build from dist-git, git, svn, and cvs
  repositories
* **Dependency resolution**: Automatically resolve dependencies between
  packages using mock's chain mode
* **Flexible installation targets**: Build for standard systems, flatpaks,
  software collections, package collections, or container images
* **Local repository management**: Automatically manage temporary or persistent
  local repositories for built packages
* **Automatic macro configuration**: Configure RPM macros automatically based
  on installation type

Why should I use rpm-build-assist?
-----------------------------------

**Simplified workflow**
  Instead of manually invoking mock for each package, define all your builds
  in a single configuration file and let rpm-build-assist handle the details.

**Consistent builds**
  Ensure consistent build environments and configurations across multiple
  packages and build runs.

**Container integration**
  Seamlessly build container images with your custom RPM packages installed,
  perfect for deployment or testing.

**Team collaboration**
  Share YAML configuration files with your team to ensure everyone builds
  packages the same way.

**CI/CD friendly**
  Simple command-line interface makes integration with CI/CD pipelines
  straightforward.

How does rpm-build-assist work?
--------------------------------

rpm-build-assist operates on a YAML configuration file that describes:

1. **Base configuration**: Which mock configuration to use for builds
2. **Build sources**: Where to fetch source code from (repositories and branches)
3. **Installation target**: How built packages should be installed or packaged

The tool then:

1. Sets up a local repository for built RPMs
2. Fetches sources from configured repositories
3. Builds each package using mock's SCM plugin
4. Stores built RPMs in the local repository (enabling dependency resolution)
5. Optionally creates installation targets (containers, etc.)

Use cases
---------

**Application development**
  Build your application and all its dependencies from source, then create a
  container image for deployment.

**Software collections**
  Create software collections with custom installation prefixes, useful for
  shipping multiple versions of the same software.

**Flatpak development**
  Build packages configured for flatpak installation with the correct prefix
  settings.

**Custom distributions**
  Build a set of related packages from various sources to create a custom
  package repository.

**Testing and CI**
  Automate package builds in CI pipelines to test changes before they're merged.

Project status
--------------

rpm-build-assist is actively developed and maintained. Features are added based
on user needs and feedback.

Current version: 1.0

License
-------

This tool is provided as-is for use in building RPM packages with mock.

Getting help
------------

* Report issues on Codeberg: https://codeberg.org/orb-project/rpm-build-assist/issues
* Check the :doc:`howto/troubleshooting` guide for common problems
* See examples in the ``examples/`` directory

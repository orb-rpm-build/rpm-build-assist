# YAML Configuration Format Reference

## Quick Reference

```yaml
base: <mock-config>
localrepo: <path>            # Optional, path to local repository directory
addrepo: <repo-url>          # Optional, additional repository URL(s)

build:
  - type: <scm-type>        # Optional, default: dist-git
    url: <base-url>          # Required
    packages:                # Required
      - <package>:<branch>   # Format: name:branch or just name

install:                     # Optional
  type: <install-type>       # Required if install section present
  collection: <name>         # Required for software-collection and package-collection types
  packages:                  # Required if install section present
    - <package-name>
```

## Field Descriptions

### base (required, string)

The mock configuration to use for building packages.

**Example values:**
- `fedora-39-x86_64`
- `fedora-40-aarch64`
- `epel-9-x86_64`
- `centos-stream-9-x86_64`

### localrepo (optional, string)

Path to a directory to use as the local repository for built RPMs.

If not specified, a temporary directory will be created automatically.

**Example values:**
- `/home/user/rpm-builds/localrepo`
- `~/builds/my-project-repo`
- `./localrepo` (relative to current directory)

**Behavior:**
- If the directory doesn't exist, it will be created automatically (including parent directories)
- If the directory exists, it will be reused (useful for incremental builds across multiple runs)
- The `--localrepo` command-line option takes precedence over this YAML setting
- If neither CLI option nor YAML config is specified, a temporary directory is created

**Use cases:**
- Preserve built RPMs between runs for faster rebuilds
- Share a repository across multiple build configurations
- Debug build issues by inspecting repository contents
- Reuse previously built dependencies without rebuilding

### addrepo (optional, string or list)

Additional repository URLs to pass to mock with the `--addrepo=` flag. This allows mock to access extra package repositories during the build process.

Can be specified as either:
- A single URL string
- A list of URL strings

**Example values:**
```yaml
# Single repository
addrepo: https://example.com/custom-repo/fedora-39-x86_64/

# Multiple repositories
addrepo:
  - https://example.com/repo1/fedora-39-x86_64/
  - https://example.com/repo2/fedora-39-x86_64/
  - https://internal.company.com/packages/
```

**Use cases:**
- Add dependencies from custom or third-party repositories
- Access build-time dependencies not available in standard repos
- Use company-internal or project-specific package repositories
- Include COPR repositories or other community repos

**Note:** The repository URLs are passed to both the source RPM build (`--buildsrpm`) and the binary RPM build (`--chain`) mock commands.

### build (required, list)

List of source repositories and packages to build.

#### Each build entry contains:

##### type (optional, string, default: "dist-git")

The SCM method to use.

**Supported values:**
- `dist-git` - Fedora/CentOS dist-git repositories
- `git` - Standard git repositories
- `svn` - Subversion repositories
- `cvs` - CVS repositories

##### url (required, string)

Base URL for the repositories. Package names will be appended to this URL.

**Examples:**
- `https://src.fedoraproject.org/rpms/`
- `https://github.com/organization/`
- `https://git.example.com/projects/`

##### packages (required, list of strings)

List of packages to build.

**Format:** `package-name:branch`
- If `:branch` is omitted, `main` is used as default
- Branch can be a branch name, tag, or commit hash

**Examples:**
```yaml
packages:
  - myapp:main
  - mylib:v1.0.0
  - another-package    # Uses 'main' branch
```

### install (optional, object)

Defines installation target and affects build configuration.

#### type (required if install present, string)

The installation target type.

**Supported values:**
- `flatpak` - Flatpak application
  - Sets RPM prefix to `/app`
- `software-collection` - Software Collection
  - Sets RPM prefix to `/opt/{collection}`
  - Requires `collection` field
- `package-collection` - Package collection with rpath library discovery
  - Sets RPM prefix to `/opt/{collection}`
  - Configures gcc LD_RUN_PATH to use rpath with $ORIGIN and $LIB for library discovery
  - Requires `collection` field
- `container` - Container image
  - Builds a container image with packages installed
  - Requires `base_image` and `tag` fields
  - Optional `registry` field for pushing to a registry
- `install-media` - Installation media/ISO (not yet implemented)
- `live-usb` - Live USB image (not yet implemented)

#### collection (required for software-collection and package-collection, string)

Name of the collection. Used to construct the installation prefix `/opt/{collection}`.

For `software-collection`, this creates a traditional software collection that typically requires
environment setup scripts or LD_LIBRARY_PATH configuration.

For `package-collection`, this creates a collection where packages have rpath configured using
$ORIGIN and $LIB, allowing binaries to find shared libraries without requiring LD_LIBRARY_PATH
or wrapper scripts.

**Examples:**
- `python311` (for software collections)
- `myapp-stack` (for package collections)

#### base_image (required for container install type, string)

Base container image to use as the starting point for the container build.

**Examples:**
- `registry.fedoraproject.org/fedora:39`
- `registry.fedoraproject.org/fedora:latest`
- `quay.io/centos/centos:stream9`
- `docker.io/library/alpine:latest`

#### tag (required for container install type, string)

Tag to assign to the built container image. Can include a registry prefix.

**Examples:**
- `myapp:latest`
- `myapp:v1.0.0`
- `company/myapp:1.0`
- `quay.io/myorg/myapp:latest`

#### registry (optional for container install type, string)

Registry to push the built image to. If specified, the image will be tagged with the registry prefix and pushed after building.

**Examples:**
- `quay.io/myorg`
- `docker.io/mycompany`
- `registry.example.com:5000/project`

**Note:** Authentication must be configured separately using `podman login` or `docker login`.

#### packages (required if install present, list of strings)

List of package names to install. Must match package names from the build section.

**Example:**
```yaml
packages:
  - myapp
  - mylib
```

## Complete Examples

### Example 1: Basic Fedora Package Build

```yaml
base: fedora-39-x86_64

build:
  - type: dist-git
    url: https://src.fedoraproject.org/rpms/
    packages:
      - htop:rawhide
      - vim:f39
```

### Example 2: Flatpak Build

```yaml
base: fedora-39-x86_64

build:
  - type: git
    url: https://github.com/myorg/
    packages:
      - myapp:v1.0

install:
  type: flatpak
  packages:
    - myapp
```

**Effect:** Packages are built with `_prefix=/app` instead of `_prefix=/usr`

### Example 3: Software Collection

```yaml
base: fedora-39-x86_64

build:
  - type: git
    url: https://internal.example.com/scl/
    packages:
      - python311:main
      - python311-pip:main

install:
  type: software-collection
  collection: python311
  packages:
    - python311
    - python311-pip
```

**Effect:** Packages are built with `_prefix=/opt/python311`

### Example 4: Container Image Build

```yaml
base: fedora-39-x86_64

build:
  # Fedora official packages
  - type: dist-git
    url: https://src.fedoraproject.org/rpms/
    packages:
      - nginx:rawhide

  # GitHub packages
  - type: git
    url: https://github.com/company/
    packages:
      - webapp:v2.0
      - webapp-plugins:v2.0

  # Internal git server
  - type: git
    url: https://git.internal.example.com/
    packages:
      - company-theme:main

install:
  type: container
  base_image: registry.fedoraproject.org/fedora:39
  tag: company/webapp:v2.0
  registry: quay.io/company
  packages:
    - nginx
    - webapp
    - webapp-plugins
    - company-theme
```

**Effect:**
1. Builds all specified packages and their dependencies
2. Creates a Containerfile based on `registry.fedoraproject.org/fedora:39`
3. Copies the local RPM repository into the container build context
4. Installs nginx, webapp, webapp-plugins, and company-theme from the local repository
5. Cleans the DNF cache to minimize image size
6. Tags the resulting image as `company/webapp:v2.0`
7. Pushes the image to `quay.io/company/webapp:v2.0`

**Result:** A container image ready to run with all custom-built packages installed

### Example 4a: Using Additional Repositories

```yaml
base: fedora-39-x86_64

# Add custom repositories for build dependencies
addrepo:
  - https://download.copr.fedorainfracloud.org/results/@company/custom-libs/fedora-39-x86_64/
  - https://repo.example.com/internal/fedora-39-x86_64/

build:
  - type: git
    url: https://github.com/company/
    packages:
      - webapp:v2.0
      - webapp-plugins:v2.0

install:
  type: container
  packages:
    - webapp
    - webapp-plugins
```

**Effect:** Mock will have access to packages from both additional repositories during the build, allowing webapp to use dependencies from the COPR repository or internal repo.

### Example 5: Package Collection Build

```yaml
base: fedora-39-x86_64

build:
  - type: git
    url: https://internal.example.com/apps/
    packages:
      - myapp:main
      - myapp-libs:main

install:
  type: package-collection
  collection: myapp-stack
  packages:
    - myapp
    - myapp-libs
```

**Effect:** Packages are built with `_prefix=/opt/myapp-stack` and LD_RUN_PATH includes `$ORIGIN/../$LIB` so that binaries can find shared libraries using both relative and absolute paths without needing to set LD_LIBRARY_PATH.

**Key Difference from Software Collections:** Unlike software collections which typically require wrapper scripts or environment modules to set LD_LIBRARY_PATH, package-collection packages have the library search path embedded directly in the binaries using gcc's rpath mechanism with GNU ld.so's `$ORIGIN` (runtime binary location) and `$LIB` (lib/lib64 platform detection) tokens.

## RPM Macro Reference

### Standard Installation Paths

By default, RPM packages use these macros:

| Macro | Default Value |
|-------|---------------|
| `_prefix` | `/usr` |
| `_exec_prefix` | `/usr` |
| `_bindir` | `/usr/bin` |
| `_sbindir` | `/usr/sbin` |
| `_libexecdir` | `/usr/libexec` |
| `_datadir` | `/usr/share` |
| `_sysconfdir` | `/etc` |
| `_localstatedir` | `/var` |
| `_libdir` | `/usr/lib` or `/usr/lib64` |
| `_includedir` | `/usr/include` |
| `_mandir` | `/usr/share/man` |
| `_infodir` | `/usr/share/info` |

### Flatpak Modifications

When `install.type: flatpak`, all paths are prefixed with `/app`:

| Macro | Flatpak Value |
|-------|---------------|
| `_prefix` | `/app` |
| `_bindir` | `/app/bin` |
| `_libdir` | `/app/lib` |
| `_datadir` | `/app/share` |
| etc. | (all prefixed with `/app`) |

### Software Collection Modifications

When `install.type: software-collection`, all paths are prefixed with `/opt/{collection}`:

Example for `collection: python311`:

| Macro | SCL Value |
|-------|-----------|
| `_prefix` | `/opt/python311` |
| `_bindir` | `/opt/python311/bin` |
| `_libdir` | `/opt/python311/lib` |
| `_datadir` | `/opt/python311/share` |
| `scl` | `python311` |

### Package Collection Modifications

When `install.type: package-collection`, all paths are prefixed with `/opt/{collection}` and build flags include rpath directives with $ORIGIN and $LIB:

Example for `collection: myapp-stack`:

| Macro | Package Collection Value |
|-------|--------------------------|
| `_prefix` | `/opt/myapp-stack` |
| `_bindir` | `/opt/myapp-stack/bin` |
| `_libdir` | `/opt/myapp-stack/lib` |
| `_datadir` | `/opt/myapp-stack/share` |
| `set_build_flags` | `%{set_build_flags} ; LD_RUN_PATH=$ORIGIN/../$LIB` |

The rpath configuration uses GNU ld.so dynamic tokens:
- `$ORIGIN` - Expands to the directory containing the binary/library at runtime
- `$LIB` - Expands to `lib` or `lib64` depending on the platform architecture

This ensures that binaries can locate shared libraries using both relative paths (via `$ORIGIN/../$LIB`) and absolute paths (via `/opt/{collection}/$LIB`) at runtime without requiring LD_LIBRARY_PATH environment variables or wrapper scripts.

## Notes

- Package names in the `install.packages` list should match the package names (not the repository names) from the `build` section
- The `base` configuration must exist in `/etc/mock/` on your system
- For dist-git, the full repository URL is constructed as `{url}{package}`
- For other git types, specify the complete URL pattern in the `url` field
- All built packages are stored in a temporary local repository for dependency resolution during chained builds

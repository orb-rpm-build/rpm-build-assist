# YAML Configuration Format Reference

## Quick Reference

```yaml
base: <mock-config>

build:
  - type: <scm-type>        # Optional, default: dist-git
    url: <base-url>          # Required
    packages:                # Required
      - <package>:<branch>   # Format: name:branch or just name

install:                     # Optional
  type: <install-type>       # Required if install section present
  collection: <name>         # Required for software-collection type
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
- `container` - Container image
- `install-media` - Installation media/ISO
- `live-usb` - Live USB image

#### collection (required for software-collection, string)

Name of the software collection. Used to construct the installation prefix `/opt/{collection}`.

**Example:** `python311`

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

### Example 4: Multiple Sources

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
  packages:
    - nginx
    - webapp
    - company-theme
```

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

## Notes

- Package names in the `install.packages` list should match the package names (not the repository names) from the `build` section
- The `base` configuration must exist in `/etc/mock/` on your system
- For dist-git, the full repository URL is constructed as `{url}{package}`
- For other git types, specify the complete URL pattern in the `url` field
- All built packages are stored in a temporary local repository for dependency resolution during chained builds

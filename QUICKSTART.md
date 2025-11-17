# Quick Start Guide

Get started with `rpm-build-assist` in 5 minutes.

## Prerequisites

1. Install dependencies:
```bash
sudo dnf install mock python3-pyyaml
```

2. Add yourself to the mock group:
```bash
sudo usermod -a -G mock $USER
```

3. **Log out and log back in** for group membership to take effect.

4. Verify mock access:
```bash
mock --version
```

## Step 1: Make the script executable

```bash
chmod +x rpm-build-assist
```

## Step 2: Create your configuration

Copy the example configuration:
```bash
cp build-assist.yaml.example my-build.yaml
```

Or create a simple configuration from scratch:
```yaml
base: fedora-39-x86_64

build:
  - type: dist-git
    url: https://src.fedoraproject.org/rpms/
    packages:
      - htop:rawhide
```

## Step 3: Run the build

```bash
# Use default build-assist.yaml
./rpm-build-assist

# Or specify your config file
./rpm-build-assist -c my-build.yaml

# Use verbose mode to see detailed progress
./rpm-build-assist -v -c my-build.yaml
```

## Step 4: Find your built packages

Built RPMs are stored in a temporary local repository. The location is printed at the end of the build:

```
INFO - Local repository preserved at: /tmp/mock-localrepo-XXXXXX
```

Look for your RPMs in that directory.

## Common Use Cases

### Build a single package from Fedora

```yaml
base: fedora-39-x86_64

build:
  - type: dist-git
    url: https://src.fedoraproject.org/rpms/
    packages:
      - htop:rawhide
```

### Build multiple related packages

```yaml
base: fedora-39-x86_64

build:
  - type: git
    url: https://github.com/myorg/
    packages:
      - myapp:v1.0
      - myapp-plugins:v1.0
      - myapp-themes:v1.0
```

The packages will be built in order and can depend on each other.

### Build for flatpak

```yaml
base: fedora-39-x86_64

build:
  - type: git
    url: https://github.com/myorg/
    packages:
      - myapp:main

install:
  type: flatpak
  packages:
    - myapp
```

This automatically configures packages to install to `/app` instead of `/usr`.

### Build a software collection

```yaml
base: fedora-39-x86_64

build:
  - type: git
    url: https://example.com/scl/
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

Packages will install to `/opt/python311` instead of `/usr`.

## Troubleshooting

### "Permission denied" errors

Make sure you're in the mock group and have logged out/in:
```bash
groups | grep mock
```

### "Configuration not found" errors

Ensure the mock configuration exists:
```bash
ls /etc/mock/fedora-39-x86_64.cfg
```

Use a different `base:` value if needed.

### See detailed error messages

Always run with `-v` to see what's happening:
```bash
./rpm-build-assist -v
```

### Check mock logs

If a build fails, check the mock logs:
```bash
ls -ltr /var/lib/mock/*/result/
```

## Next Steps

- Read [README.md](README.md) for complete documentation
- See [YAML-FORMAT.md](YAML-FORMAT.md) for configuration reference
- Check [build-assist.yaml.example](build-assist.yaml.example) for more examples

## Getting Help

Run the program with `--help` to see all options:
```bash
./rpm-build-assist --help
```

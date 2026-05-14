Install Types Reference
=======================

This page provides detailed information about each install type.

Overview
--------

Install types determine:

1. What RPM macros are set during build
2. What post-build artifacts are created
3. Where files are installed in the filesystem

Available types
---------------

flatpak
-------

**Purpose**: Build packages for flatpak applications

**Prefix**: ``/app``

**RPM Macros**:

.. code-block:: text

   _prefix = /app
   _exec_prefix = /app
   _bindir = /app/bin
   _sbindir = /app/sbin
   _libexecdir = /app/libexec
   _datadir = /app/share
   _sysconfdir = /etc
   _localstatedir = /var
   _libdir = /app/lib or /app/lib64
   _includedir = /app/include
   _mandir = /app/share/man
   _infodir = /app/share/info

**Use case**: Building RPMs that will be installed into a flatpak runtime

**Configuration**:

.. code-block:: yaml

   install:
     type: flatpak
     packages:
       - myapp

**Post-build**: No additional artifacts created; packages are just built with
flatpak macros

software-collection
-------------------

**Purpose**: Build traditional software collections

**Prefix**: ``/opt/{collection}``

**RPM Macros**:

.. code-block:: text

   _prefix = /opt/{collection}
   _exec_prefix = /opt/{collection}
   _bindir = /opt/{collection}/bin
   _sbindir = /opt/{collection}/sbin
   _libexecdir = /opt/{collection}/libexec
   _datadir = /opt/{collection}/share
   _sysconfdir = /etc
   _localstatedir = /var
   _libdir = /opt/{collection}/lib or lib64
   _includedir = /opt/{collection}/include
   scl = {collection}

**Use case**: Installing multiple versions of software side-by-side

**Configuration**:

.. code-block:: yaml

   install:
     type: software-collection
     collection: python311
     packages:
       - python311
       - python311-pip

**Post-build**: No additional artifacts

**Runtime requirements**: Requires environment setup to use:

.. code-block:: bash

   export PATH=/opt/python311/bin:$PATH
   export LD_LIBRARY_PATH=/opt/python311/lib64:$LD_LIBRARY_PATH

**Advantages**:

* Standard SCL format
* Can use existing SCL tooling
* Environment modules support

**Disadvantages**:

* Requires environment setup
* Needs wrapper scripts or modules

package-collection
------------------

**Purpose**: Build self-contained package collections with automatic library
resolution

**Prefix**: ``/opt/{collection}``

**RPM Macros**:

.. code-block:: text

   _prefix = /opt/{collection}
   (same as software-collection)

   Plus:
   set_build_flags appends: LD_RUN_PATH=$ORIGIN/../$LIB

**RPATH configuration**: Automatically adds RPATH to binaries using:

* ``$ORIGIN`` - Directory containing the binary
* ``$LIB`` - Platform-specific lib directory (lib or lib64)

**Use case**: Self-contained applications that don't need environment setup

**Configuration**:

.. code-block:: yaml

   install:
     type: package-collection
     collection: myapp-stack
     packages:
       - myapp
       - myapp-libs

**Post-build**: No additional artifacts

**Runtime requirements**: None - binaries find libraries automatically

**How RPATH works**:

For a binary at ``/opt/myapp-stack/bin/myapp``:

* ``$ORIGIN`` resolves to ``/opt/myapp-stack/bin``
* ``$ORIGIN/../$LIB`` resolves to ``/opt/myapp-stack/lib64``
* Libraries are found without LD_LIBRARY_PATH

**Advantages**:

* No environment setup needed
* Binaries "just work"
* Simple user experience

**Disadvantages**:

* Build system must respect LDFLAGS
* Only works for compiled binaries (not scripts)
* RPATH can be overridden by LD_LIBRARY_PATH

**Verification**:

Check that RPATH is set:

.. code-block:: bash

   readelf -d /opt/myapp-stack/bin/myapp | grep RPATH

container
---------

**Purpose**: Build container images with custom RPMs installed

**Base**: User-specified container image

**Configuration**:

.. code-block:: yaml

   install:
     type: container
     base_image: registry.fedoraproject.org/fedora:39
     tag: myapp:v1.0
     registry: quay.io/myorg  # Optional
     packages:
       - myapp
       - nginx

Build Methods
~~~~~~~~~~~~~

The container install type supports two build methods:

**containerfile** (default)
  Traditional Containerfile-based build. Runs DNF inside the container during build.

  * Base image must include DNF
  * Creates intermediate layers with DNF cache
  * Works with podman or docker
  * General-purpose, works with any base image

**buildah**
  Uses buildah mount + dnf --installroot. Runs DNF on the host, installing into the mounted container filesystem.

  * Base image does not need DNF (or anything at all)
  * Can bootstrap from completely empty scratch image
  * No intermediate DNF layers
  * Results in minimal final images containing only specified packages
  * Requires buildah installed
  * Ideal for production images (scratch, fedora-minimal)

**Comparison**:

.. list-table::
   :header-rows: 1
   :widths: 20 40 40

   * - Aspect
     - containerfile
     - buildah
   * - Base image requirements
     - Must include DNF
     - No requirements (can use scratch)
   * - Build speed
     - DNF runs in container
     - DNF runs on host
   * - Image size
     - Larger (includes base OS)
     - Minimal (only specified packages)
   * - Dependencies
     - podman or docker
     - buildah
   * - Use case
     - General purpose
     - Production, truly minimal images

**Example with buildah (scratch-based)**:

.. code-block:: yaml

   install:
     type: container
     build_method: buildah
     base_image: scratch
     tag: myapp:minimal
     releasever: "40"
     install_weak_deps: false  # Exclude weak dependencies
     packages:
       - myapp
       - bash              # For container shell
       - coreutils-single  # Basic utilities

**Post-build**: Container image built and optionally pushed to registry

**Process (containerfile method)**:

1. Copies local RPM repository to build context
2. Generates Containerfile with bind mount:

   .. code-block:: dockerfile

      FROM {base_image}
      RUN --mount=type=bind,source=localrepo,target=/tmp/localrepo ...
      RUN dnf install -y {packages} && dnf clean all

3. Builds image with podman or docker
4. Tags as specified
5. Pushes to registry if specified

**Process (buildah method)**:

1. Creates working container from base image (``buildah from``)
2. Mounts container filesystem (``buildah mount``)
3. Runs ``dnf install --installroot=<mountpoint>`` from host
4. Unmounts container (``buildah unmount``)
5. Commits to final image (``buildah commit``)
6. Pushes to registry if specified

**Container runtime**: Automatically detects podman, docker, or buildah

**Use cases**:

* Application deployment
* Testing built packages
* Distributing via container registries

**Requirements**:

* containerfile method: podman or docker installed
* buildah method: buildah installed
* For registry push: authenticated to registry

**Example Containerfile** (generated):

.. code-block:: dockerfile

   FROM registry.fedoraproject.org/fedora:39

   COPY localrepo /tmp/localrepo

   RUN echo -e '[localrepo]\n\
   name=Local Repository\n\
   baseurl=file:///tmp/localrepo\n\
   enabled=1\n\
   gpgcheck=0' > /etc/yum.repos.d/localrepo.repo

   RUN dnf install -y myapp nginx && \
       dnf clean all && \
       rm -rf /var/cache/dnf /tmp/localrepo /etc/yum.repos.d/localrepo.repo

**Best practices**:

* Use specific base image tags
* Minimize layer size
* Don't include secrets
* Scan for vulnerabilities

Comparison table
----------------

.. list-table::
   :header-rows: 1
   :widths: 15 15 15 15 20 20

   * - Type
     - Prefix
     - RPATH
     - Env Setup
     - Artifacts
     - Use Case
   * - flatpak
     - /app
     - No
     - No
     - None
     - Flatpak runtimes
   * - software-collection
     - /opt/{name}
     - No
     - Yes
     - None
     - Multiple versions
   * - package-collection
     - /opt/{name}
     - Yes
     - No
     - None
     - Self-contained apps
   * - container
     - /usr
     - No
     - No
     - Image
     - Deployment

Not yet implemented
-------------------

install-media
~~~~~~~~~~~~~

**Status**: Planned

**Purpose**: Create bootable installation media with custom packages

live-usb
~~~~~~~~

**Status**: Planned

**Purpose**: Create live USB images with custom packages

See also
--------

* :doc:`../tutorial/software_collections` - Tutorial on collections
* :doc:`../tutorial/container_builds` - Container build tutorial
* :doc:`../format/install_section` - Configuration reference

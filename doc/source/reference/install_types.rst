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

**Post-build**: Container image built and optionally pushed to registry

**Process**:

1. Copies local RPM repository to build context
2. Generates Containerfile:

   .. code-block:: dockerfile

      FROM {base_image}
      COPY localrepo /tmp/localrepo
      RUN echo '[localrepo]...' > /etc/yum.repos.d/localrepo.repo
      RUN dnf install -y {packages} && dnf clean all && rm -rf ...

3. Builds image with podman or docker
4. Tags as specified
5. Pushes to registry if specified

**Container runtime**: Automatically detects podman or docker

**Use cases**:

* Application deployment
* Testing built packages
* Distributing via container registries

**Requirements**:

* podman or docker installed
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

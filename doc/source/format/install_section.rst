Install Section Reference
=========================

The ``install`` section defines how built packages should be installed or
packaged. This section is optional.

Overview
--------

If present, the install section:

1. Affects the build process by setting RPM macros
2. May create additional artifacts (container images, etc.)
3. Specifies which packages to install

Structure
---------

.. code-block:: yaml

   install:
     type: <install-type>
     <type-specific-fields>
     packages:
       - <package-name>

Common fields
-------------

type
~~~~

**Required**: Yes (if install section present)

**Type**: String

**Description**: The installation target type.

**Supported values**:

* ``flatpak`` - Flatpak application
* ``software-collection`` - Software collection
* ``package-collection`` - Package collection with rpath
* ``container`` - Container image
* ``install-media`` - Installation media (not yet implemented)
* ``live-usb`` - Live USB image (not yet implemented)

See :doc:`../reference/install_types` for detailed descriptions.

packages
~~~~~~~~

**Required**: Yes (if install section present)

**Type**: List of strings

**Description**: List of package names to install. Must match package names
from the build section.

**Example**:

.. code-block:: yaml

   packages:
     - myapp
     - mylib
     - mytools

Install types
-------------

flatpak
~~~~~~~

Configures packages for flatpak installation.

**Fields**:

* ``type``: Must be ``flatpak``
* ``packages``: List of packages

**Effect**: Sets RPM macros to install to ``/app`` prefix instead of ``/usr``.

**Example**:

.. code-block:: yaml

   install:
     type: flatpak
     packages:
       - myapp

**RPM macros set**:

* ``_prefix`` → ``/app``
* ``_bindir`` → ``/app/bin``
* ``_libdir`` → ``/app/lib``
* ``_datadir`` → ``/app/share``

software-collection
~~~~~~~~~~~~~~~~~~~

Builds a traditional software collection.

**Fields**:

* ``type``: Must be ``software-collection``
* ``collection``: Name of the collection (required)
* ``packages``: List of packages

**Effect**: Sets RPM macros to install to ``/opt/{collection}`` prefix.

**Example**:

.. code-block:: yaml

   install:
     type: software-collection
     collection: python311
     packages:
       - python311
       - python311-pip

**RPM macros set**:

* ``_prefix`` → ``/opt/python311``
* ``_bindir`` → ``/opt/python311/bin``
* ``_libdir`` → ``/opt/python311/lib``
* ``scl`` → ``python311``

**Usage**: Requires environment setup (PATH, LD_LIBRARY_PATH) to use.

package-collection
~~~~~~~~~~~~~~~~~~

Builds a package collection with automatic library resolution via RPATH.

**Fields**:

* ``type``: Must be ``package-collection``
* ``collection``: Name of the collection (required)
* ``packages``: List of packages

**Effect**: Sets RPM macros to install to ``/opt/{collection}`` and configures
RPATH for library discovery.

**Example**:

.. code-block:: yaml

   install:
     type: package-collection
     collection: myapp-stack
     packages:
       - myapp
       - myapp-libs

**RPM macros set**:

* ``_prefix`` → ``/opt/myapp-stack``
* ``_bindir`` → ``/opt/myapp-stack/bin``
* ``set_build_flags`` → Includes ``LD_RUN_PATH=$ORIGIN/../$LIB``

**Difference from software-collection**: Binaries work without environment
setup because library paths are embedded via RPATH.

container
~~~~~~~~~

Builds a container image with packages installed.

**Fields**:

* ``type``: Must be ``container``
* ``base_image``: Base container image (required)
* ``tag``: Image tag (required)
* ``registry``: Registry to push to (optional)
* ``packages``: List of packages

**Effect**: Creates a container image with packages installed from the local
repository.

**Example**:

.. code-block:: yaml

   install:
     type: container
     base_image: registry.fedoraproject.org/fedora:39
     tag: myapp:v1.0
     registry: quay.io/myorg
     packages:
       - myapp
       - nginx

**Process**:

1. Builds all packages
2. Copies local repository to build context
3. Generates Containerfile
4. Builds container image
5. Tags image
6. Pushes to registry (if specified)

**Container runtime**: Automatically detects podman or docker.

Field reference by type
-----------------------

flatpak
~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 20 15 65

   * - Field
     - Required
     - Description
   * - type
     - Yes
     - Must be ``flatpak``
   * - packages
     - Yes
     - List of package names

software-collection
~~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 20 15 65

   * - Field
     - Required
     - Description
   * - type
     - Yes
     - Must be ``software-collection``
   * - collection
     - Yes
     - Name of the collection
   * - packages
     - Yes
     - List of package names

package-collection
~~~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 20 15 65

   * - Field
     - Required
     - Description
   * - type
     - Yes
     - Must be ``package-collection``
   * - collection
     - Yes
     - Name of the collection
   * - packages
     - Yes
     - List of package names

container
~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 20 15 65

   * - Field
     - Required
     - Description
   * - type
     - Yes
     - Must be ``container``
   * - build_method
     - No
     - Build method: ``containerfile`` (default) or ``buildah``. Use buildah for minimal base images.
   * - base_image
     - Yes
     - Base container image
   * - tag
     - Yes
     - Tag for resulting image
   * - releasever
     - No
     - Release version for DNF (buildah method only). Example: ``"40"``. If not specified, DNF will attempt to detect from base image.
   * - registry
     - No
     - Registry to push to
   * - packages
     - Yes
     - List of package names

Examples
--------

Flatpak build
~~~~~~~~~~~~~

.. code-block:: yaml

   base: fedora-39-x86_64

   build:
     - url: https://github.com/myorg/
       packages:
         - myapp:main

   install:
     type: flatpak
     packages:
       - myapp

Software collection
~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   base: fedora-39-x86_64

   build:
     - url: https://internal.example.com/scl/
       packages:
         - python311:main
         - python311-pip:main

   install:
     type: software-collection
     collection: python311
     packages:
       - python311
       - python311-pip

Container image
~~~~~~~~~~~~~~~

.. code-block:: yaml

   base: fedora-39-x86_64

   build:
     - type: dist-git
       url: https://src.fedoraproject.org/rpms/
       packages:
         - nginx:rawhide

     - type: git
       url: https://github.com/company/
       packages:
         - webapp:v2.0

   install:
     type: container
     base_image: registry.fedoraproject.org/fedora:39
     tag: company/webapp:v2.0
     registry: quay.io/company
     packages:
       - nginx
       - webapp

Container with buildah (minimal image)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   base: fedora-40-x86_64

   build:
     - type: git
       url: https://github.com/company/
       packages:
         - myapp:main

   install:
     type: container
     build_method: buildah
     base_image: registry.fedoraproject.org/fedora-minimal:40
     tag: company/myapp:minimal
     releasever: "40"
     packages:
       - myapp

Best practices
--------------

Match packages to build list
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Only list packages that are in the build section:

.. code-block:: yaml

   build:
     - url: https://github.com/myorg/
       packages:
         - myapp:main
         - mylib:main

   install:
     packages:
       - myapp     # OK
       - mylib     # OK
       - other     # ERROR: not in build section

Include runtime dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For container builds, you can include packages not built by rpm-build-assist:

.. code-block:: yaml

   install:
     type: container
     packages:
       - myapp          # Built by rpm-build-assist
       - python3        # From base image repos
       - nginx          # From base image repos

These external packages are installed from the base image's repositories.

Use specific collection names
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For collections, use descriptive, versioned names:

.. code-block:: yaml

   # Good
   collection: python311
   collection: nodejs20
   collection: myapp-v2

   # Less clear
   collection: python
   collection: node

Version container tags
~~~~~~~~~~~~~~~~~~~~~~

Use specific versions for container tags:

.. code-block:: yaml

   # Good
   tag: myapp:v1.0.0
   tag: myapp:2024-05-03

   # Avoid
   tag: myapp:latest

Common issues
-------------

Package not found
~~~~~~~~~~~~~~~~~

**Error**: Package listed in install.packages not found

**Cause**: Package name doesn't match any built package

**Solution**: Verify package names match the build section exactly

Registry push fails
~~~~~~~~~~~~~~~~~~~

**Error**: Failed to push container image

**Solutions**:

* Authenticate: ``podman login <registry>``
* Verify registry URL format
* Check network connectivity
* Verify permissions to push to registry

Container runtime not found
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Error**: Neither podman nor docker found

**Solution**: Install podman or docker:

.. code-block:: bash

   sudo dnf install podman

RPATH not working
~~~~~~~~~~~~~~~~~

**Problem**: Package collection binaries can't find libraries

**Causes**:

* Build system doesn't respect LDFLAGS
* Binary is a script (scripts don't have RPATH)

**Solution**: Ensure build system uses compiler flags correctly

Next steps
----------

* See :doc:`../tutorial/software_collections` for collection examples
* Read :doc:`../tutorial/container_builds` for container workflows
* Check :doc:`../reference/install_types` for detailed type descriptions

Building from Mixed Sources
============================

This guide shows how to build packages from multiple source repositories and
types in a single configuration.

Use case
--------

You want to build:

* Some packages from Fedora dist-git
* Your custom application from GitHub
* Internal libraries from a private git server

All in one build, with proper dependency resolution.

Basic example
-------------

.. code-block:: yaml

   base: fedora-39-x86_64

   build:
     # Fedora packages
     - type: dist-git
       url: https://src.fedoraproject.org/rpms/
       packages:
         - nginx:rawhide
         - postgresql:f39

     # GitHub packages
     - type: git
       url: https://github.com/mycompany/
       packages:
         - webapp:v2.0
         - webapp-plugins:v2.0

     # Internal packages
     - type: git
       url: https://git.internal.example.com/
       packages:
         - company-theme:main
         - company-branding:release

This builds six packages from three different sources.

Dependency ordering
-------------------

Packages are built in the order they appear. If later packages depend on
earlier ones, list dependencies first:

.. code-block:: yaml

   build:
     # Base libraries (no dependencies)
     - type: git
       url: https://github.com/myorg/
       packages:
         - base-lib:v1.0
         - utils-lib:v1.0

     # Middle tier (depends on base libraries)
     - type: git
       url: https://github.com/myorg/
       packages:
         - middleware:v2.0

     # Application (depends on middleware)
     - type: dist-git
       url: https://src.fedoraproject.org/rpms/
       packages:
         - nginx:rawhide

     - type: git
       url: https://github.com/myorg/
       packages:
         - webapp:v2.0

Cross-repository dependencies
------------------------------

Dependencies can span repositories:

.. code-block:: yaml

   build:
     # Build foundation from Fedora
     - type: dist-git
       url: https://src.fedoraproject.org/rpms/
       packages:
         - python3:rawhide
         - python3-pip:rawhide

     # Build custom Python packages
     - type: git
       url: https://github.com/myorg/
       packages:
         - python3-mylib:main      # Needs python3
         - python3-myapp:main      # Needs python3-mylib

All packages end up in the local repository, so later builds find them.

Using addrepo for external dependencies
----------------------------------------

If you need packages not built by rpm-build-assist:

.. code-block:: yaml

   base: fedora-39-x86_64

   # Add COPR repository
   addrepo: https://download.copr.fedorainfracloud.org/results/@company/libs/

   build:
     - type: git
       url: https://github.com/myorg/
       packages:
         - myapp:main  # Can use packages from COPR repo

Multiple addrepo URLs:

.. code-block:: yaml

   addrepo:
     - https://example.com/repo1/
     - https://example.com/repo2/
     - https://download.copr.fedorainfracloud.org/results/@company/libs/

Complex example
---------------

A real-world configuration with multiple sources, dependencies, and a
container image:

.. code-block:: yaml

   base: fedora-39-x86_64
   localrepo: ./localrepo

   addrepo:
     - https://download.copr.fedorainfracloud.org/results/@company/custom-libs/

   build:
     # System libraries from Fedora
     - type: dist-git
       url: https://src.fedoraproject.org/rpms/
       packages:
         - nginx:rawhide
         - postgresql:f39
         - redis:rawhide

     # Custom shared libraries
     - type: git
       url: https://github.com/mycompany/libraries/
       packages:
         - libmyapp-core:v3.0
         - libmyapp-utils:v3.0

     # Internal authentication library
     - type: git
       url: https://git.internal.example.com/security/
       packages:
         - libauth:v1.2.0

     # Main application
     - type: git
       url: https://github.com/mycompany/
       packages:
         - webapp-backend:v2.5.0
         - webapp-frontend:v2.5.0

     # Plugins (depend on backend)
     - type: git
       url: https://github.com/mycompany/plugins/
       packages:
         - webapp-plugin-analytics:v1.0
         - webapp-plugin-reporting:v1.0

     # Configuration packages
     - type: git
       url: https://git.internal.example.com/ops/
       packages:
         - company-branding:main
         - company-config:production

   install:
     type: container
     base_image: registry.fedoraproject.org/fedora:39
     tag: mycompany/webapp:v2.5.0
     registry: quay.io/mycompany
     packages:
       - nginx
       - postgresql
       - redis
       - webapp-backend
       - webapp-frontend
       - webapp-plugin-analytics
       - webapp-plugin-reporting
       - company-branding
       - company-config

This builds 14 packages from 5 different sources and creates a container image.

Best practices
--------------

Group by source
~~~~~~~~~~~~~~~

Keep packages from the same repository together:

.. code-block:: yaml

   # Good
   build:
     - url: https://github.com/org/
       packages:
         - pkg1:main
         - pkg2:main
         - pkg3:main

   # Works but verbose
   build:
     - url: https://github.com/org/
       packages:
         - pkg1:main
     - url: https://github.com/org/
       packages:
         - pkg2:main

Document dependencies in comments
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   build:
     - url: https://github.com/myorg/
       packages:
         # Core library (no deps)
         - libcore:v1.0

         # Utilities (requires libcore)
         - libutils:v1.0

         # Application (requires both)
         - myapp:v2.0

Use consistent versioning
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   # Good: consistent versioning
   packages:
     - component-a:v2.0
     - component-b:v2.0
     - component-c:v2.0

   # Harder to track
   packages:
     - component-a:main
     - component-b:v1.5
     - component-c:abc123

Test incrementally
~~~~~~~~~~~~~~~~~~

When setting up a complex multi-source build:

1. Start with one source
2. Verify it builds
3. Add next source
4. Verify dependencies resolve
5. Continue until complete

Use localrepo for development
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

During development, use a persistent local repository:

.. code-block:: yaml

   localrepo: ./dev-builds

This avoids rebuilding unchanged packages.

Troubleshooting
---------------

Dependency not found
~~~~~~~~~~~~~~~~~~~~

**Problem**: Later package can't find earlier package

**Causes**:

* Packages in wrong order
* Package name mismatch
* Earlier build failed

**Solutions**:

* Check build order
* Verify exact package names
* Check mock logs for earlier failures

Build succeeds but install fails
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Problem**: Build completes but container/install fails

**Cause**: Package listed in ``install.packages`` that wasn't built

**Solution**: Verify all install packages are in the build list

Mixed architecture issues
~~~~~~~~~~~~~~~~~~~~~~~~~

**Problem**: Some packages build for wrong architecture

**Cause**: Using different mock configs or arch-specific branches

**Solution**: Ensure all packages use the same base config

Private repository access
~~~~~~~~~~~~~~~~~~~~~~~~~

**Problem**: Can't access private repositories

**Solutions**:

* Ensure SSH keys are set up
* Use HTTPS with credentials
* Configure git credential helper

Performance considerations
--------------------------

Parallel builds
~~~~~~~~~~~~~~~

rpm-build-assist builds sequentially. For faster builds with independent
packages, you could run multiple instances:

.. code-block:: bash

   # Terminal 1: Build set A
   ./rpm-build-assist -c set-a.yaml --localrepo ./shared-repo

   # Terminal 2: Build set B (independent of A)
   ./rpm-build-assist -c set-b.yaml --localrepo ./shared-repo

Both use the same local repository.

Incremental builds
~~~~~~~~~~~~~~~~~~

Use a persistent localrepo to avoid rebuilding:

.. code-block:: yaml

   localrepo: ~/rpm-cache/myproject

Once a package is built, it won't be rebuilt unless you delete it from the
localrepo.

See also
--------

* :doc:`../format/build_section` - Build section reference
* :doc:`persistent_repos` - Managing local repositories
* :doc:`troubleshooting` - Common issues

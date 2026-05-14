.. _tutorial_container_builds:

Building Container Images
==========================

This tutorial shows how to use rpm-build-assist to build RPM packages and
automatically create container images with those packages installed.

Prerequisites
-------------

* Complete the :doc:`first_build` tutorial
* Install podman or docker:

  .. code-block:: bash

     sudo dnf install podman

Use case
--------

You want to build your application from source, package it as an RPM, and
create a container image ready for deployment. All in one command.

Step 1: Basic container build
------------------------------

Create a ``build-assist.yaml`` file:

.. code-block:: yaml

   base: fedora-39-x86_64

   build:
     - type: dist-git
       url: https://src.fedoraproject.org/rpms/
       packages:
         - nginx:rawhide

   install:
     type: container
     base_image: registry.fedoraproject.org/fedora:39
     tag: my-nginx:latest
     packages:
       - nginx

Run the build:

.. code-block:: bash

   ./rpm-build-assist -v

What happens
~~~~~~~~~~~~

rpm-build-assist will:

1. Build the nginx package using mock
2. Store the RPM in a local repository
3. Create a Containerfile that:

   * Starts from ``registry.fedoraproject.org/fedora:39``
   * Sets up a DNF repository pointing to the local RPMs
   * Installs nginx
   * Cleans up the DNF cache

4. Build the container image using podman or docker
5. Tag it as ``my-nginx:latest``

Verify the image
~~~~~~~~~~~~~~~~

Check that the image was created:

.. code-block:: bash

   podman images | grep my-nginx

Run the container:

.. code-block:: bash

   podman run -it my-nginx:latest nginx -v

You should see the nginx version from your built RPM.

Step 2: Building custom packages
---------------------------------

Let's build a custom application and create a container for it:

.. code-block:: yaml

   base: fedora-39-x86_64

   build:
     - type: git
       url: https://github.com/myorg/
       packages:
         - myapp:v1.0

   install:
     type: container
     base_image: registry.fedoraproject.org/fedora:39
     tag: mycompany/myapp:v1.0
     packages:
       - myapp

This builds ``myapp`` from a git repository and packages it into a container.

Step 3: Multiple packages in one image
---------------------------------------

You can install multiple packages into a single container:

.. code-block:: yaml

   base: fedora-39-x86_64

   build:
     - type: dist-git
       url: https://src.fedoraproject.org/rpms/
       packages:
         - nginx:rawhide
         - postgresql:rawhide

     - type: git
       url: https://github.com/myorg/
       packages:
         - webapp:v2.0
         - webapp-plugins:v2.0

   install:
     type: container
     base_image: registry.fedoraproject.org/fedora:39
     tag: mycompany/webapp:v2.0
     packages:
       - nginx
       - postgresql
       - webapp
       - webapp-plugins

This creates a container image with all four packages installed.

Build order matters
~~~~~~~~~~~~~~~~~~~

Packages are built in the order listed. If ``webapp`` depends on
``webapp-plugins``, list ``webapp-plugins`` first.

Step 4: Pushing to a registry
------------------------------

To push your built image to a container registry, add the ``registry`` field:

.. code-block:: yaml

   base: fedora-39-x86_64

   build:
     - type: git
       url: https://github.com/myorg/
       packages:
         - myapp:v1.0

   install:
     type: container
     base_image: registry.fedoraproject.org/fedora:39
     tag: myapp:v1.0
     registry: quay.io/myorg
     packages:
       - myapp

Before running the build, authenticate to your registry:

.. code-block:: bash

   podman login quay.io

Run the build:

.. code-block:: bash

   ./rpm-build-assist -v

The image will be:

1. Built and tagged as ``myapp:v1.0``
2. Tagged as ``quay.io/myorg/myapp:v1.0``
3. Pushed to ``quay.io/myorg/myapp:v1.0``

Step 5: Using different base images
------------------------------------

You can use any base image:

Minimal images
~~~~~~~~~~~~~~

.. code-block:: yaml

   install:
     type: container
     base_image: registry.fedoraproject.org/fedora-minimal:39
     tag: myapp:minimal
     packages:
       - myapp

RHEL/UBI images
~~~~~~~~~~~~~~~

.. code-block:: yaml

   install:
     type: container
     base_image: registry.access.redhat.com/ubi9/ubi
     tag: myapp:ubi9
     packages:
       - myapp

Custom base images
~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   install:
     type: container
     base_image: company-registry.example.com/base:latest
     tag: myapp:latest
     packages:
       - myapp

Step 6: Adding runtime dependencies
------------------------------------

Your application might need packages that aren't built by you:

.. code-block:: yaml

   base: fedora-39-x86_64

   build:
     - type: git
       url: https://github.com/myorg/
       packages:
         - myapp:v1.0

   install:
     type: container
     base_image: registry.fedoraproject.org/fedora:39
     tag: myapp:v1.0
     packages:
       - myapp
       # These will be installed from Fedora repos
       - python3
       - python3-flask
       - python3-sqlalchemy

Packages not built by rpm-build-assist will be installed from the base
image's configured repositories.

Understanding the Containerfile
--------------------------------

When you use ``type: container``, rpm-build-assist generates a Containerfile
like this:

.. code-block:: dockerfile

   FROM registry.fedoraproject.org/fedora:39

   COPY localrepo /tmp/localrepo

   RUN echo -e '[localrepo]\n\
   name=Local Repository\n\
   baseurl=file:///tmp/localrepo\n\
   enabled=1\n\
   gpgcheck=0' > /etc/yum.repos.d/localrepo.repo

   RUN dnf install -y myapp && \
       dnf clean all && \
       rm -rf /var/cache/dnf /tmp/localrepo /etc/yum.repos.d/localrepo.repo

This:

1. Uses your specified base image
2. Copies the local RPM repository into the image
3. Configures DNF to use the local repository
4. Installs your packages
5. Cleans up to minimize image size

Advanced: Custom Containerfile
-------------------------------

If you need more control, you can provide your own Containerfile and just use
rpm-build-assist to build the RPMs:

1. Build without install section:

   .. code-block:: yaml

      base: fedora-39-x86_64
      localrepo: ./localrepo

      build:
        - type: git
          url: https://github.com/myorg/
          packages:
            - myapp:v1.0

2. Create your own Containerfile:

   .. code-block:: dockerfile

      FROM registry.fedoraproject.org/fedora:39

      COPY localrepo /tmp/localrepo
      RUN dnf install -y --repofrompath=local,/tmp/localrepo myapp

      # Your custom steps here
      EXPOSE 8080
      CMD ["/usr/bin/myapp"]

3. Build the container manually:

   .. code-block:: bash

      podman build -t myapp:custom .

Building Minimal Container Images
----------------------------------

For production deployments, you may want to minimize container image size by
building from scratch with only the packages you need. The ``buildah`` build
method enables this by using DNF on the host to install into an empty
container filesystem.

When to use buildah
~~~~~~~~~~~~~~~~~~~

Use the buildah build method when:

* You want the absolute smallest image size
* Building from scratch with only required packages
* Building production images where every megabyte counts
* You don't need a base OS - just your application and its dependencies

Use the default containerfile method when:

* You want simplicity and compatibility
* Using standard base images (fedora, ubi, etc.)
* The base image already includes DNF and base utilities
* You don't have buildah available

How it works
~~~~~~~~~~~~

The buildah method uses a different approach:

1. **Creates a working container** from the base image (even scratch) using ``buildah from``
2. **Mounts the container filesystem** to a directory on the host
3. **Runs DNF on the host** with ``--installroot`` pointing to the mount
4. **DNF bootstraps** the container with only the specified packages and dependencies
5. **Commits the result** to a final image

This means DNF never runs inside the container and can bootstrap a complete
filesystem from scratch.

Example: Truly minimal scratch-based image
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create a configuration building from scratch:

.. code-block:: yaml

   # minimal-container.yaml
   base: fedora-40-x86_64

   build:
     - type: git
       url: https://github.com/myorg/
       packages:
         - myapp:v1.0

   install:
     type: container
     build_method: buildah
     base_image: scratch
     tag: myapp:minimal-v1.0
     releasever: "40"
     install_weak_deps: false  # Exclude weak dependencies
     packages:
       - myapp
       - bash              # Minimal shell
       - coreutils-single  # Basic utilities

Build the image:

.. code-block:: bash

   ./rpm-build-assist -c minimal-container.yaml

The ``releasever`` field is required for the buildah method to tell DNF which
Fedora release to use when resolving dependencies.

Setting ``install_weak_deps: false`` excludes recommended-but-not-required
packages (weak dependencies), further reducing image size. This is similar to
using ``--no-install-recommends`` in other package managers.

Size comparison
~~~~~~~~~~~~~~~

Compare image sizes between methods:

.. code-block:: bash

   # Standard containerfile method with fedora base
   # Base: ~190 MB, Final: ~830 MB (with dependencies)

   # Buildah method with scratch base
   # Base: 0 MB, Final: ~650 MB (only what's needed)

The buildah method with scratch eliminates all base OS overhead, including
over 100 packages you don't need. The final image contains only:

* Your application packages
* Their runtime dependencies
* Minimal utilities you explicitly specify

Requirements
~~~~~~~~~~~~

The buildah method requires:

* buildah installed on your build system
* SELinux contexts properly configured (buildah handles this automatically)
* Sufficient permissions to mount filesystems

Install buildah:

.. code-block:: bash

   sudo dnf install buildah

Verification
~~~~~~~~~~~~

After building, verify the image:

.. code-block:: bash

   # Check image size
   podman images myapp:minimal-v1.0

   # Count installed packages
   podman run myapp:minimal-v1.0 rpm -qa | wc -l

   # Verify only specified packages are present
   podman run myapp:minimal-v1.0 rpm -qa | grep -E 'myapp|bash|coreutils'

   # Verify no base OS packages
   podman run myapp:minimal-v1.0 which dnf
   # Should fail - dnf is not installed

   # Test your application
   podman run myapp:minimal-v1.0 /usr/bin/myapp --version

Best practices
--------------

Use specific tags
~~~~~~~~~~~~~~~~~

Always use specific version tags, not ``latest``:

.. code-block:: yaml

   tag: myapp:v1.0.0

This makes it clear which version is deployed.

Minimize layer size
~~~~~~~~~~~~~~~~~~~

The generated Containerfile already minimizes layers by combining install and
cleanup steps.

Use .containerignore
~~~~~~~~~~~~~~~~~~~~

If you're building containers manually, create a ``.containerignore`` to
exclude unnecessary files from the build context.

Security considerations
~~~~~~~~~~~~~~~~~~~~~~~

* Use trusted base images
* Keep base images updated
* Scan images for vulnerabilities
* Don't include secrets in the image

Testing containers
------------------

After building, test your container:

.. code-block:: bash

   # Run interactively
   podman run -it myapp:v1.0 /bin/bash

   # Check installed packages
   podman run myapp:v1.0 rpm -qa | grep myapp

   # Test the application
   podman run -p 8080:8080 myapp:v1.0

Troubleshooting
---------------

Container runtime not found
~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you see:

.. code-block:: text

   ERROR: Neither podman nor docker found

Install podman:

.. code-block:: bash

   sudo dnf install podman

Failed to push to registry
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Ensure you're authenticated:

.. code-block:: bash

   podman login registry.example.com

And that you have permission to push to that registry.

DNF install fails in container
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Check the mock build logs to ensure your RPMs were built successfully. The
container build fails if the RPMs are missing or corrupted.

Next steps
----------

* Learn about :doc:`software_collections` for custom installation prefixes
* Read :doc:`../howto/mixed_sources` for complex build scenarios
* See :doc:`../reference/install_types` for all installation type options

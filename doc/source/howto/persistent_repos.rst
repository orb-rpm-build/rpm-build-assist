Using Persistent Repositories
==============================

This guide explains how to use persistent local repositories effectively.

Why use persistent repositories?
---------------------------------

By default, rpm-build-assist creates a temporary directory for the local
repository. This directory is deleted when the system reboots.

Persistent repositories offer several benefits:

* **Preserve builds**: Keep built RPMs between runs
* **Faster rebuilds**: Avoid rebuilding unchanged packages
* **Easy access**: RPMs remain available for installation or inspection
* **Shareable**: Can be used as a DNF repository
* **Debuggable**: Inspect contents between builds

Specifying a repository
------------------------

In YAML configuration
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   base: fedora-39-x86_64
   localrepo: /path/to/repo

   build:
     # ...

On command line
~~~~~~~~~~~~~~~

.. code-block:: bash

   ./rpm-build-assist --localrepo /path/to/repo

The command-line option overrides the YAML setting.

Recommended locations
---------------------

User home directory
~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   localrepo: ~/rpm-builds/myproject

Good for personal development.

Project directory
~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   localrepo: ./localrepo

Keeps builds with project. Add to ``.gitignore``:

.. code-block:: text

   localrepo/
   *.rpm
   *.src.rpm

Shared location
~~~~~~~~~~~~~~~

.. code-block:: yaml

   localrepo: /var/cache/rpm-build-assist/myproject

Good for team sharing (requires permissions).

Repository structure
--------------------

A local repository contains:

.. code-block:: text

   localrepo/
   ├── package1-1.0-1.fc39.x86_64.rpm
   ├── package1-1.0-1.fc39.src.rpm
   ├── package2-2.0-1.fc39.x86_64.rpm
   ├── package2-2.0-1.fc39.src.rpm
   └── repodata/
       ├── repomd.xml
       ├── primary.xml.gz
       ├── filelists.xml.gz
       └── other.xml.gz

The ``repodata/`` directory is created by ``createrepo_c`` (via mock).

Managing repositories
---------------------

Viewing contents
~~~~~~~~~~~~~~~~

.. code-block:: bash

   # List RPMs
   ls -lh localrepo/*.rpm

   # Query packages
   rpm -qp localrepo/myapp-*.rpm

   # Show package info
   dnf info localrepo/myapp-*.rpm

Cleaning old packages
~~~~~~~~~~~~~~~~~~~~~

Remove specific packages:

.. code-block:: bash

   rm localrepo/myapp-*.rpm

Remove all packages:

.. code-block:: bash

   rm localrepo/*.rpm
   rm -rf localrepo/repodata

Rebuilding repository metadata
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you manually add/remove RPMs:

.. code-block:: bash

   createrepo_c localrepo/

Using as a DNF repository
--------------------------

Local file repository
~~~~~~~~~~~~~~~~~~~~~

Create a DNF repo file:

.. code-block:: bash

   cat > /etc/yum.repos.d/mybuilds.repo <<EOF
   [mybuilds]
   name=My Built Packages
   baseurl=file:///home/user/rpm-builds/myproject
   enabled=1
   gpgcheck=0
   EOF

Now you can install packages:

.. code-block:: bash

   sudo dnf install myapp

HTTP repository
~~~~~~~~~~~~~~~

Serve the repository over HTTP:

.. code-block:: bash

   cd localrepo
   python3 -m http.server 8000

Configure clients:

.. code-block:: ini

   [mybuilds]
   name=My Built Packages
   baseurl=http://buildserver:8000
   enabled=1
   gpgcheck=0

Incremental builds
------------------

With a persistent repository, packages are not rebuilt if they already exist.

To force a rebuild:

1. Delete the package from localrepo:

   .. code-block:: bash

      rm localrepo/myapp-*.rpm

2. Run rpm-build-assist again

Alternatively, delete the entire repository to rebuild everything:

.. code-block:: bash

   rm -rf localrepo/

Sharing repositories
--------------------

Between developers
~~~~~~~~~~~~~~~~~~

Use a shared network location:

.. code-block:: yaml

   localrepo: /mnt/shared/rpm-builds/project

Ensure all developers have read/write access.

With CI/CD
~~~~~~~~~~

Cache the repository between CI runs:

.. code-block:: yaml

   # GitLab CI example
   cache:
     paths:
       - localrepo/

   build:
     script:
       - ./rpm-build-assist --localrepo ./localrepo

Best practices
--------------

Use descriptive names
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   # Good
   localrepo: ~/rpm-builds/webapp-v2
   localrepo: ./builds/production

   # Less clear
   localrepo: ./repo
   localrepo: ~/rpms

Version in path
~~~~~~~~~~~~~~~

Include version or date in path:

.. code-block:: yaml

   localrepo: ~/rpm-builds/myproject-2024-05-03
   localrepo: ~/rpm-builds/myproject-v2.0

Separate repos for different configs
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: yaml

   # development.yaml
   localrepo: ./builds/development

   # production.yaml
   localrepo: ./builds/production

This prevents mixing dev and production packages.

Regular cleanup
~~~~~~~~~~~~~~~

Old RPMs accumulate. Clean periodically:

.. code-block:: bash

   # Delete RPMs older than 30 days
   find localrepo/ -name "*.rpm" -mtime +30 -delete
   createrepo_c localrepo/

Backup important builds
~~~~~~~~~~~~~~~~~~~~~~~

For releases, backup the repository:

.. code-block:: bash

   tar czf webapp-v2.0-rpms.tar.gz localrepo/

Troubleshooting
---------------

Permission denied
~~~~~~~~~~~~~~~~~

**Problem**: Can't write to localrepo directory

**Solutions**:

* Check directory permissions
* Create directory manually: ``mkdir -p /path/to/repo``
* Use a directory you own

Repository corruption
~~~~~~~~~~~~~~~~~~~~~

**Problem**: "Repository metadata corrupt" errors

**Solution**: Rebuild metadata:

.. code-block:: bash

   rm -rf localrepo/repodata
   createrepo_c localrepo/

Disk space
~~~~~~~~~~

**Problem**: Repository grows too large

**Solutions**:

* Clean old packages regularly
* Use different repositories for different projects
* Store only final RPMs (delete intermediate builds)

stale packages
~~~~~~~~~~~~~~

**Problem**: Old version of package in repository

**Solution**: Remove old RPMs and rebuild:

.. code-block:: bash

   rm localrepo/myapp-1.0-*.rpm
   ./rpm-build-assist

Advanced usage
--------------

Signing packages
~~~~~~~~~~~~~~~~

Sign RPMs in the repository:

.. code-block:: bash

   rpm --addsign localrepo/*.rpm

Update repository metadata to include signatures:

.. code-block:: bash

   createrepo_c localrepo/

Creating an archive
~~~~~~~~~~~~~~~~~~~

Archive a build for distribution:

.. code-block:: bash

   cd localrepo
   tar czf ../myproject-rpms.tar.gz *.rpm repodata/

Mirroring to remote
~~~~~~~~~~~~~~~~~~~~

Sync to a remote server:

.. code-block:: bash

   rsync -avz localrepo/ user@server:/var/www/html/repos/myproject/

Multiple architectures
~~~~~~~~~~~~~~~~~~~~~~

Separate repositories by architecture:

.. code-block:: yaml

   # x86_64 build
   base: fedora-39-x86_64
   localrepo: ./builds/x86_64

   # aarch64 build (separate config)
   base: fedora-39-aarch64
   localrepo: ./builds/aarch64

See also
--------

* :doc:`mixed_sources` - Building from multiple sources
* :doc:`../format/yaml_format` - Configuration reference
* ``createrepo_c`` man page for repository management

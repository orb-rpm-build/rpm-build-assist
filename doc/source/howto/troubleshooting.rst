Troubleshooting Guide
=====================

This guide covers common problems and their solutions.

Installation issues
-------------------

Permission denied when running mock
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Symptom**:

.. code-block:: text

   ERROR: You must be root or a member of the mock group

**Solution**:

1. Add yourself to the mock group:

   .. code-block:: bash

      sudo usermod -a -G mock $USER

2. Log out completely and log back in

3. Verify group membership:

   .. code-block:: bash

      groups | grep mock

PyYAML not found
~~~~~~~~~~~~~~~~

**Symptom**:

.. code-block:: text

   ModuleNotFoundError: No module named 'yaml'

**Solution**:

.. code-block:: bash

   # Fedora/RHEL
   sudo dnf install python3-pyyaml

   # Debian/Ubuntu
   sudo apt-get install python3-yaml

Configuration errors
--------------------

YAML syntax error
~~~~~~~~~~~~~~~~~

**Symptom**:

.. code-block:: text

   ERROR: YAML syntax error

**Common causes**:

* Mixing tabs and spaces (use spaces only)
* Incorrect indentation
* Unclosed quotes
* Invalid YAML structure

**Solution**: Validate your YAML:

.. code-block:: bash

   python3 -c "import yaml; yaml.safe_load(open('build-assist.yaml'))"

Missing required field
~~~~~~~~~~~~~~~~~~~~~~

**Symptom**:

.. code-block:: text

   ERROR: 'base' is required
   ERROR: 'url' is required

**Solution**: Add the missing field to your configuration.

Mock configuration not found
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Symptom**:

.. code-block:: text

   ERROR: Could not find configuration file

**Solution**:

1. Check available configs:

   .. code-block:: bash

      ls /etc/mock/*.cfg

2. Use the filename without ``.cfg``:

   .. code-block:: yaml

      base: fedora-39-x86_64  # Not fedora-39-x86_64.cfg

Build failures
--------------

Package not found
~~~~~~~~~~~~~~~~~

**Symptom**:

.. code-block:: text

   ERROR: Could not find package at URL

**Solutions**:

* Verify URL construction: check that ``{url}{package}`` is correct
* Test in browser: visit the URL
* Check spelling of package name
* Verify branch/tag exists

Build dependency not found
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Symptom**: Mock reports missing build dependencies

**Solutions**:

1. Ensure dependency is in build list and comes before dependent package

2. Use ``addrepo`` for external dependencies:

   .. code-block:: yaml

      addrepo: https://example.com/repo/

3. Check that earlier package builds succeeded

4. Verify package names match exactly

Spec file not found
~~~~~~~~~~~~~~~~~~~

**Symptom**:

.. code-block:: text

   ERROR: Could not find spec file

**For git repositories**:

* Ensure ``{package}.spec`` exists in repository root
* Spec filename must match package name exactly

**Solution**:

.. code-block:: bash

   # Repository layout should be:
   myapp/
   └── myapp.spec  # Must be in root

Build fails with compilation errors
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Symptom**: Build fails during compilation

**This is usually not an rpm-build-assist issue**. The package itself has
build problems.

**Debug**:

1. Check mock logs:

   .. code-block:: bash

      less /var/lib/mock/fedora-39-x86_64/result/build.log

2. Look for compilation errors, missing headers, etc.

3. Fix the package source code or spec file

Container issues
----------------

Container runtime not found
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Symptom**:

.. code-block:: text

   ERROR: Neither podman nor docker found

**Solution**:

.. code-block:: bash

   sudo dnf install podman

Failed to build container image
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Symptom**: Container build fails

**Check**:

1. Do the RPMs exist?

   .. code-block:: bash

      ls localrepo/*.rpm

2. Are package names correct in ``install.packages``?

3. Check container build logs

Failed to push to registry
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Symptom**:

.. code-block:: text

   ERROR: Failed to push container image

**Solutions**:

1. Authenticate:

   .. code-block:: bash

      podman login quay.io

2. Verify registry URL format

3. Check network connectivity

4. Verify push permissions

DNF install fails in container
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Symptom**: Container build fails during package installation

**Causes**:

* RPM is corrupted or missing
* Dependencies can't be resolved
* Base image repos are down

**Debug**:

1. Verify RPMs are valid:

   .. code-block:: bash

      rpm -qp localrepo/myapp-*.rpm

2. Try installing locally:

   .. code-block:: bash

      sudo dnf install localrepo/myapp-*.rpm

Repository issues
-----------------

Can't write to localrepo
~~~~~~~~~~~~~~~~~~~~~~~~~

**Symptom**:

.. code-block:: text

   ERROR: Permission denied: localrepo/

**Solutions**:

* Check directory permissions
* Create directory: ``mkdir -p localrepo``
* Use a directory you own

Repository metadata corrupt
~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Symptom**:

.. code-block:: text

   ERROR: Repository metadata corrupt

**Solution**: Rebuild metadata:

.. code-block:: bash

   rm -rf localrepo/repodata
   createrepo_c localrepo/

Old package version used
~~~~~~~~~~~~~~~~~~~~~~~~

**Symptom**: Build uses old version of a dependency

**Cause**: Old RPM is in local repository

**Solution**: Remove old RPM and rebuild:

.. code-block:: bash

   rm localrepo/oldpackage-*.rpm
   ./rpm-build-assist

Performance issues
------------------

Builds are slow
~~~~~~~~~~~~~~~

**Solutions**:

1. Use persistent localrepo to avoid rebuilding

2. Use mock's cache (enabled by default)

3. Reduce number of packages

4. Use faster storage for localrepo and mock cache

Running out of disk space
~~~~~~~~~~~~~~~~~~~~~~~~~

**Solutions**:

1. Clean mock cache:

   .. code-block:: bash

      mock --scrub=all

2. Clean old localrepo builds:

   .. code-block:: bash

      rm -rf localrepo/

3. Clean old mock roots:

   .. code-block:: bash

      sudo rm -rf /var/lib/mock/*/root/

Network issues
--------------

Can't access private repositories
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**For private git repositories**:

1. Ensure SSH keys are set up

2. Or use HTTPS with credentials:

   .. code-block:: bash

      git config --global credential.helper store

3. Test access manually:

   .. code-block:: bash

      git clone {repository-url}

Source download fails
~~~~~~~~~~~~~~~~~~~~~

**Symptom**: Can't download sources

**Solutions**:

* Check network connectivity
* Verify repository URL is accessible
* Check proxy settings
* Use ``addrepo`` if downloading from custom location

Debug workflow
--------------

Step-by-step debugging
~~~~~~~~~~~~~~~~~~~~~~

1. **Enable verbose mode**:

   .. code-block:: bash

      ./rpm-build-assist -v

2. **Check configuration**:

   Validate YAML syntax is correct

3. **Verify URLs**:

   Manually check that repository URLs are accessible

4. **Check mock logs**:

   .. code-block:: bash

      less /var/lib/mock/{config}/result/build.log

5. **Build manually with mock**:

   Try building one package manually to isolate the issue

Test with simple package
~~~~~~~~~~~~~~~~~~~~~~~~~

Start with a known-good package:

.. code-block:: yaml

   base: fedora-39-x86_64

   build:
     - type: dist-git
       url: https://src.fedoraproject.org/rpms/
       packages:
         - htop:rawhide

If this works, the issue is with your custom packages.

Getting help
------------

Collect information
~~~~~~~~~~~~~~~~~~~

When asking for help, provide:

1. Your configuration file
2. Full error message
3. Verbose output (``-v`` flag)
4. Mock logs if relevant
5. rpm-build-assist version
6. Operating system and version

Where to ask
~~~~~~~~~~~~

* Codeberg issues: https://codeberg.org/orb-project/rpm-build-assist/issues
* Include all information listed above

Known limitations
-----------------

* Builds are sequential (no parallel builds)
* Limited to mock-supported platforms
* Requires network access for source checkout
* No offline mode

See also
--------

* :doc:`../main_using` - User guide
* :doc:`mixed_sources` - Complex build scenarios
* :doc:`persistent_repos` - Repository management
* ``mock`` documentation for mock-specific issues

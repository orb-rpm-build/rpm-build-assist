Name:           rpm-build-assist
Version:        0.1.0
Release:        1%{?dist}
Summary:        Tool for orchestrating RPM package builds using mock
Source:         rpm-build-assist-%{version}.tar.gz

License:        GPLv3+
URL:            https://codeberg.org/orb-project/rpm-build-assist

BuildArch:      noarch

Requires:       python3
Requires:       python3-pyyaml
Requires:       mock

# Container install type is optional
Suggests:       podman

# Needed to expand %%autorelease / %%autochangelog in dist-git packages
Recommends:     rpmautospec

BuildRequires:  python3-devel

%description
rpm-build-assist is a Python tool for orchestrating RPM package builds from
source control repositories using mock. It supports building from various SCM
types (git, dist-git, CVS, SVN) and can install built packages into different
environments including containers, flatpak prefixes, and software collections.

Key features:
- Declarative YAML configuration
- Leverages mock's SCM plugin for source checkout
- Chain builds with dependency resolution via package repositories
- Multiple installation types: standard, container, flatpak, SCL
- Auto-detection of podman or docker for container builds

%prep
# When built via mock SCM, sources are already in place
# No %setup needed

%build
# Nothing to build - it's a single Python script

%install
install -D -m 0755 rpm-build-assist %{buildroot}%{_bindir}/rpm-build-assist
install -D -m 0755 rpm-build-assist-src-get %{buildroot}%{_libexecdir}/rpm-build-assist/src-get

%files
%{_bindir}/rpm-build-assist
%{_libexecdir}/rpm-build-assist/
%doc README.md README-DOCS.md examples/

%changelog
* Sun May 03 2026 Gordon Messmer <gordon.messmer@gmail.com> - 0.1.0-1
- Initial package

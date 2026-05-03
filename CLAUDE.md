# Claude Development Guide for rpm-build-assist

## Project Overview

rpm-build-assist is a Python tool for orchestrating RPM package builds from source control repositories using mock.

**Key design principles:**
- Declarative YAML configuration
- Leverage mock's existing capabilities (don't reinvent)
- Support multiple workflows (containers, flatpaks, SCLs, etc.)
- External dependencies are acceptable if they simplify the project

**Official repository:** https://codeberg.org/orb-project/rpm-build-assist

## Architecture Decisions

### Mock Integration
We use mock's SCM plugin for source checkout and building. Don't reimplement source fetching or building - pass appropriate options to mock and let it handle the details.

### YAML Configuration
Configuration is pure YAML - no custom DSL, no Python in configs. Keep it simple and declarative.

### Package Repository Pattern
All builds use a package repository (temporary or persistent) for dependency resolution. This repository may be on the local filesystem, or could be shared among a cluster of hosts. This is managed via mock's `--localrepo` and `--chain` options.

## Code Conventions

### Python Compatibility
- **Target: Python 3.6+** for broad compatibility
- External dependencies are acceptable if they simplify the project
- Current external dependencies: PyYAML

### Code Style
- Follow PEP 8
- Use descriptive variable names
- Keep functions focused and readable
- Add docstrings to complex functions

### Error Handling
- Validate YAML configuration early
- Provide clear error messages to users
- Exit with appropriate status codes (0 = success, 1 = failure)

## Documentation Structure

### User Documentation (Sphinx)
Located in `doc/source/`, organized as:

- **`tutorial/`** - Learning-oriented, step-by-step guides
  - first_build.rst - Getting started
  - container_builds.rst - Container image workflows
  - software_collections.rst - SCL and package collection builds

- **`howto/`** - Problem-oriented, specific tasks
  - mixed_sources.rst - Building from multiple repos
  - persistent_repos.rst - Managing local repositories
  - troubleshooting.rst - Common issues and solutions

- **`reference/`** - Information-oriented, technical descriptions
  - command_line.rst - CLI options
  - install_types.rst - All installation types
  - scm_types.rst - All SCM types

- **`format/`** - Configuration reference
  - yaml_format.rst - Top-level format
  - build_section.rst - Build section details
  - install_section.rst - Install section details

### When Adding Features

**Always update documentation when adding features:**

1. **New install type:**
   - Add to `reference/install_types.rst`
   - Add to `format/install_section.rst`
   - Consider adding tutorial if complex

2. **New SCM type:**
   - Add to `reference/scm_types.rst`
   - Update `format/build_section.rst`

3. **New CLI option:**
   - Add to `reference/command_line.rst`
   - Update `main_using.rst` if it changes workflow

4. **New YAML field:**
   - Add to appropriate `format/*.rst` file
   - Add or update relevant example in `examples/`

### Documentation Best Practices

- **Test examples** - Every code example should be tested
- **Be specific** - Use real URLs, not "example.com" when showing dist-git
- **Link between docs** - Use `:doc:` references liberally
- **Update README.md** - If user-facing behavior changes significantly
- **Keep README.md focused** - It's a project overview, not a manual

### Building Documentation

Always test doc builds before committing documentation changes:

```bash
./build-docs
# Check for warnings in output
xdg-open doc/build/html/index.html
```

Fix any Sphinx warnings - they indicate broken references or formatting issues.

## Development Workflow

### Making Changes

1. **Understand the impact** - Changes to mock invocation affect all build types
2. **Test thoroughly** - Run actual mock builds with the change
3. **Update docs** - Documentation changes go with code changes in same commit
4. **Check examples** - Ensure examples in `examples/` still work

### Testing Changes

**Before committing:**

1. **Test documentation:**
   ```bash
   ./build-docs
   # Check for warnings
   ```

2. **Verify examples:**
   - Ensure relevant examples in `examples/` demonstrate the feature
   - Add new example files for new installation types

### Commit Conventions

**Good commit messages:**
- Start with verb: "Add", "Fix", "Update", "Remove"
- Be specific: "Add support for CVS repositories" not "Add feature"
- Include "Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>" at the end

**Commit granularity:**
- Code + related docs in same commit
- Don't mix unrelated changes
- Each commit should be a logical unit

## Common Tasks

### Adding a New Installation Type

1. Implement the installation type in the codebase
2. Update `doc/source/reference/install_types.rst` with full description
3. Update `doc/source/format/install_section.rst` with YAML fields
4. Create a dedicated example file in `examples/` demonstrating the installation type
5. Consider adding tutorial if workflow is complex

### Adding a New SCM Type

1. Mock handles most SCM types, just validate the type value in the codebase
2. Update `doc/source/reference/scm_types.rst` with full details
3. Update `doc/source/format/build_section.rst`
4. Add or update relevant example in `examples/`

### Adding a Command-Line Option

1. Add to the argument parser in the codebase
2. Update `doc/source/reference/command_line.rst`
3. Update `doc/source/main_using.rst` if it changes typical usage

## Important Implementation Notes

### Mock Configuration
- Always pass `--chain` for dependency resolution
- Use `--scm-enable` and `--scm-option` for source control
- Let mock handle source checkout - don't reimplement
- Pass `--localrepo` to enable the package repository

### RPM Macros
- Macros are passed to mock via `--macro` options
- Different install types set different prefixes
- Always use standard RPM macro names (`_prefix`, `_bindir`, etc.)
- See `_get_macros_for_install_type()` for pattern

### Container Builds
- Auto-detect podman or docker
- Generate Containerfile, don't use pre-written templates
- Clean up DNF cache to minimize image size
- Use `:Z` flag on volume mounts for SELinux compatibility

### Error Messages
- Be specific: "Package 'htop' not found at https://..." not just "Package not found"
- Suggest solutions: "Ensure you're in the mock group: groups | grep mock"
- Show paths to logs when builds fail

## What NOT to Do

### Don't:
- ❌ Reimplement mock's source fetching
- ❌ Put user documentation in CLAUDE.md (use doc/source/)
- ❌ Skip documentation updates when adding features
- ❌ Commit generated files (doc/build/)
- ❌ Hard-code paths to mock configs (let user specify in YAML)
- ❌ Make breaking changes to YAML format without discussion

### Do:
- ✅ Keep the code simple and readable
- ✅ Use mock's capabilities whenever possible
- ✅ Validate YAML configuration early with clear errors
- ✅ Update documentation alongside code
- ✅ Add external dependencies if they simplify the project
- ✅ Maintain backwards compatibility when possible
- ✅ Ask user before destructive operations (like force-pushing containers)

## Special Considerations

### Backwards Compatibility
- YAML format changes require careful consideration
- Old configs should continue to work when possible
- If breaking changes needed, document migration path

### Security
- Never execute arbitrary code from YAML
- Be careful with paths (don't write outside intended areas)
- Container registry credentials are user's responsibility

### Dependencies
- mock must be installed on the system
- PyYAML for configuration parsing
- podman or docker needed for container install type
- Additional dependencies are acceptable if they simplify the project

## File Organization

```
rpm-build-assist/
├── rpm-build-assist           # Main entry point (currently a single script)
├── build-docs                 # Doc build script
├── README.md                  # Project overview (keep concise)
├── README-DOCS.md            # Quick doc reference
├── CLAUDE.md                 # This file
├── .readthedocs.yaml         # Read the Docs config
├── examples/                  # Example configurations
│   ├── README.md
│   └── *.yaml                # One example per installation type
└── doc/                       # Sphinx documentation
    ├── source/               # .rst files (29 files)
    │   ├── index.rst        # Doc homepage
    │   ├── tutorial/        # Step-by-step guides
    │   ├── howto/           # Task-oriented guides
    │   ├── reference/       # Technical reference
    │   └── format/          # YAML format reference
    ├── BUILD.md             # How to build docs
    ├── PUBLISHING.md        # How to publish docs
    └── README.md            # Doc overview
```

## Testing Checklist

Before committing, verify:

- [ ] Code runs without Python errors
- [ ] Documentation builds without warnings: `./build-docs`
- [ ] New features have documentation
- [ ] YAML format changes are documented
- [ ] Commit message is clear and specific
- [ ] No generated files committed (doc/build/)

## Getting Help

If you need to understand how something works:

1. Read the codebase to understand existing patterns
2. Check mock documentation for SCM plugin options
3. Review the documentation structure
4. Look at examples in `examples/` directory

## Future Considerations

Features planned but not yet implemented are mentioned in documentation with:
```rst
.. note::

   This feature is planned for a future version.
```

Don't implement "planned" features without user confirmation - they're aspirational, not committed.

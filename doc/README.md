# rpm-build-assist Documentation

This directory contains the Sphinx-based documentation for rpm-build-assist.

## Building the Documentation Locally

### Install dependencies

```bash
# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Build HTML documentation

```bash
make html
```

The generated documentation will be in `build/html/`. Open `build/html/index.html` in your browser.

### Serve locally

After building, you can serve the documentation locally:

```bash
make serve
```

Then visit http://localhost:8000

### Clean build artifacts

```bash
make clean
```

## Documentation Structure

```
doc/
├── source/
│   ├── conf.py              # Sphinx configuration
│   ├── index.rst            # Documentation home
│   ├── main_*.rst           # Main user guide sections
│   ├── tutorial/            # Step-by-step tutorials
│   ├── format/              # Configuration format reference
│   ├── reference/           # Command-line and type references
│   └── howto/               # How-to guides
├── requirements.txt         # Python dependencies
├── Makefile                 # Build automation
└── README.md               # This file
```

## Documentation Style

- Use reStructuredText (.rst) format
- Follow the [Divio documentation system](https://documentation.divio.com/):
  - **Tutorials**: Learning-oriented, step-by-step lessons
  - **How-to guides**: Problem-oriented, specific tasks
  - **Reference**: Information-oriented, technical descriptions
  - **Explanation**: Understanding-oriented, background and context

## Contributing

When adding new features to rpm-build-assist:

1. Update relevant reference documentation
2. Add how-to guides for new capabilities
3. Update tutorials if user workflows change
4. Keep examples up-to-date

## Publishing

See [PUBLISHING.md](PUBLISHING.md) for detailed instructions on publishing
the documentation to various platforms.

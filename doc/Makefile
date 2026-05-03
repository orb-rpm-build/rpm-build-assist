# Makefile for Sphinx documentation

# You can set these variables from the command line
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = source
BUILDDIR      = build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile clean

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

clean:
	rm -rf $(BUILDDIR)/*

# Convenience targets
html-fast:
	@$(SPHINXBUILD) -b html "$(SOURCEDIR)" "$(BUILDDIR)/html" -W --keep-going

serve:
	@echo "Serving documentation at http://localhost:8000"
	@cd $(BUILDDIR)/html && python3 -m http.server 8000

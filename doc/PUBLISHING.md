# Publishing rpm-build-assist Documentation

This guide explains how to publish the rpm-build-assist documentation to various platforms.

## Table of Contents

- [Option 1: Read the Docs (Recommended)](#option-1-read-the-docs-recommended)
- [Option 2: GitHub Pages](#option-2-github-pages)
- [Option 3: GitLab Pages](#option-3-gitlab-pages)
- [Option 4: Self-Hosted](#option-4-self-hosted)
- [Comparison of Options](#comparison-of-options)

---

## Option 1: Read the Docs (Recommended)

**Best for**: Open source projects, free hosting, automatic builds

### Advantages
- Free for public projects
- Automatic builds on git push
- Multiple versions supported
- Built-in search
- PDF/EPUB generation
- Custom domain support
- SSL included

### Setup

1. **Create account** at https://readthedocs.org

2. **Import your project**:
   - Click "Import a Project"
   - Connect your GitHub/GitLab account
   - Select the rpm-build-assist repository

3. **Create `.readthedocs.yaml`** in repository root:

   ```yaml
   # .readthedocs.yaml
   version: 2

   build:
     os: ubuntu-22.04
     tools:
       python: "3.11"

   sphinx:
     configuration: doc/source/conf.py
     fail_on_warning: false

   python:
     install:
       - requirements: doc/requirements.txt
   ```

4. **Commit and push**:
   ```bash
   git add .readthedocs.yaml
   git commit -m "Add Read the Docs configuration"
   git push
   ```

5. **Build automatically**: Read the Docs will automatically build on each push

6. **Access documentation**: 
   - Default: `https://rpm-build-assist.readthedocs.io`
   - Custom domain: Configure in project settings

### Versioning

Read the Docs builds docs for each git tag/branch:

```bash
# Create a release tag
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

Users can switch between versions in the docs.

### Custom Domain

1. In Read the Docs project settings → Domains
2. Add your custom domain (e.g., `docs.rpm-build-assist.org`)
3. Create CNAME record pointing to `rpm-build-assist.readthedocs.io`

---

## Option 2: GitHub Pages

**Best for**: GitHub-hosted projects, simple deployment

### Advantages
- Free hosting
- Integrated with GitHub
- Custom domains supported
- SSL included

### Disadvantages
- Manual build process (or CI/CD required)
- No automatic multi-version support
- Limited to static HTML

### Setup with GitHub Actions (Automated)

1. **Create GitHub Actions workflow** at `.github/workflows/docs.yml`:

   ```yaml
   name: Build and Deploy Docs

   on:
     push:
       branches: [ main ]
     pull_request:
       branches: [ main ]

   jobs:
     build:
       runs-on: ubuntu-latest
       
       steps:
       - uses: actions/checkout@v3
       
       - name: Set up Python
         uses: actions/setup-python@v4
         with:
           python-version: '3.11'
       
       - name: Install dependencies
         run: |
           pip install -r doc/requirements.txt
       
       - name: Build documentation
         run: |
           cd doc
           make html
       
       - name: Deploy to GitHub Pages
         if: github.event_name == 'push' && github.ref == 'refs/heads/main'
         uses: peaceiris/actions-gh-pages@v3
         with:
           github_token: ${{ secrets.GITHUB_TOKEN }}
           publish_dir: ./doc/build/html
   ```

2. **Enable GitHub Pages**:
   - Repository Settings → Pages
   - Source: Deploy from a branch
   - Branch: `gh-pages` / `root`

3. **Commit and push**:
   ```bash
   git add .github/workflows/docs.yml
   git commit -m "Add documentation build workflow"
   git push
   ```

4. **Access docs**: `https://orb-project.codeberg.page/rpm-build-assist/` (or your configured Pages URL)

### Setup Manually

1. **Build documentation**:
   ```bash
   cd doc
   make html
   ```

2. **Install ghp-import** (one-time):
   ```bash
   pip install ghp-import
   ```

3. **Deploy to GitHub Pages**:
   ```bash
   ghp-import -n -p -f doc/build/html
   ```

4. **Enable GitHub Pages** in repository settings

---

## Option 3: GitLab Pages

**Best for**: GitLab-hosted projects

### Advantages
- Free hosting
- Integrated with GitLab CI/CD
- Custom domains
- SSL included

### Setup

1. **Create `.gitlab-ci.yml`** in repository root:

   ```yaml
   pages:
     image: python:3.11
     
     before_script:
       - pip install -r doc/requirements.txt
     
     script:
       - cd doc
       - make html
       - mv build/html ../public
     
     artifacts:
       paths:
         - public
     
     only:
       - main
   ```

2. **Commit and push**:
   ```bash
   git add .gitlab-ci.yml
   git commit -m "Add GitLab Pages configuration"
   git push
   ```

3. **Access docs**: `https://orb-project.gitlab.io/rpm-build-assist/` (or your configured Pages URL)

---

## Option 4: Self-Hosted

**Best for**: Internal documentation, custom requirements

### Using nginx

1. **Build documentation**:
   ```bash
   ./build-docs
   ```

2. **Copy to web server**:
   ```bash
   scp -r doc/build/html/* user@server:/var/www/html/docs/rpm-build-assist/
   ```

3. **Configure nginx**:
   ```nginx
   server {
       listen 80;
       server_name docs.example.com;
       
       root /var/www/html/docs/rpm-build-assist;
       index index.html;
       
       location / {
           try_files $uri $uri/ =404;
       }
   }
   ```

4. **Access docs**: `http://docs.example.com`

### Using Apache

1. **Build and copy** (same as nginx)

2. **Configure Apache**:
   ```apache
   <VirtualHost *:80>
       ServerName docs.example.com
       DocumentRoot /var/www/html/docs/rpm-build-assist
       
       <Directory /var/www/html/docs/rpm-build-assist>
           Options Indexes FollowSymLinks
           AllowOverride None
           Require all granted
       </Directory>
   </VirtualHost>
   ```

### Docker Container (Optional)

If you want to serve docs in a container:

```dockerfile
FROM nginx:alpine
COPY doc/build/html /usr/share/nginx/html
EXPOSE 80
```

Build the docs first, then the container:

```bash
./build-docs
docker build -t rpm-build-assist-docs -f- . <<EOF
FROM nginx:alpine
COPY doc/build/html /usr/share/nginx/html
EOF
docker run -d -p 8080:80 rpm-build-assist-docs
```

Access at `http://localhost:8080`

---

## Comparison of Options

| Feature | Read the Docs | GitHub Pages | GitLab Pages | Self-Hosted |
|---------|---------------|--------------|--------------|-------------|
| **Cost** | Free | Free | Free | Server costs |
| **Setup Difficulty** | Easy | Medium | Easy | Hard |
| **Auto Build** | Yes | With Actions | With CI/CD | Manual/CI |
| **Versioning** | Built-in | Manual | Manual | Manual |
| **Search** | Built-in | No | No | Need to add |
| **PDF/EPUB** | Built-in | No | No | No |
| **Custom Domain** | Yes | Yes | Yes | Yes |
| **SSL** | Free | Free | Free | Need to setup |
| **Private Docs** | Paid | Private repo | Private repo | Yes |

## Recommended Approach

**For public projects**:
1. **Primary**: Read the Docs (best features, free)
2. **Backup**: GitHub Pages (simple fallback)

**For private/internal projects**:
- Small teams: GitHub/GitLab Pages with private repo
- Large organizations: Self-hosted with access control

## Multi-Version Documentation

### Read the Docs
Handles automatically - builds each branch/tag.

### GitHub Pages Manual
Create version selector:

```bash
# Build v1.0
git checkout v1.0
cd doc && make html
ghp-import -n -p -f -b gh-pages-v1.0 doc/build/html

# Build v2.0
git checkout v2.0
cd doc && make html
ghp-import -n -p -f -b gh-pages-v2.0 doc/build/html
```

Add version switcher in `conf.py`.

## Updating Documentation

### Read the Docs
Automatically rebuilds on push to repository.

### GitHub/GitLab Pages
Automatically rebuilds with CI/CD on push.

### Self-Hosted
1. Pull latest code
2. Rebuild docs: `./build-docs`
3. Copy to server: `scp -r doc/build/html/* user@server:/path/`

Or set up CI/CD to do this automatically.

## Best Practices

1. **Use Read the Docs for public projects** - It's free and feature-rich

2. **Automate builds** - Use CI/CD, don't build manually

3. **Version your docs** - Users need docs for the version they're using

4. **Custom domain** - `docs.rpm-build-assist.org` is more professional than `rpm-build-assist.readthedocs.io`

5. **Test builds locally** before pushing:
   ```bash
   ./build-docs
   xdg-open doc/build/html/index.html  # Linux
   open doc/build/html/index.html  # macOS
   ```

6. **Monitor broken links**:
   ```bash
   cd doc
   sphinx-build -b linkcheck source build/linkcheck
   ```

7. **Keep dependencies updated**:
   ```bash
   pip list --outdated
   pip install --upgrade sphinx sphinx-rtd-theme
   ```

## Troubleshooting

### Build fails with "command not found: sphinx-build"
```bash
pip install -r doc/requirements.txt
```

### Import errors
Ensure `doc/requirements.txt` includes all dependencies.

### Theme not found
```bash
pip install sphinx-rtd-theme
```

### Read the Docs build fails
- Check build logs in Read the Docs dashboard
- Verify `.readthedocs.yaml` is correct
- Ensure `conf.py` path is correct

### GitHub Pages not updating
- Check Actions logs for errors
- Ensure `gh-pages` branch exists
- Verify Pages settings in repository

## Next Steps

After publishing:

1. **Add documentation badge** to README:
   ```markdown
   [![Documentation](https://readthedocs.org/projects/rpm-build-assist/badge/)](https://rpm-build-assist.readthedocs.io)
   ```

2. **Link from main repo** - Add prominent link in README

3. **Announce** - Let users know documentation is available

4. **Keep updated** - Update docs with each release

5. **Monitor analytics** - See what pages users visit most

6. **Collect feedback** - Add feedback mechanism in docs

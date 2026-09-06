# GitHub Upload / First Commit

GitHub does not automatically unpack a `.tar.gz` uploaded through the normal web file uploader. Extract the archive first, then commit the repository contents.

```bash
tar -xzf execution-finality-rats-reference-v0.1.0.tar.gz
cd execution-finality-rats-reference
python -m unittest discover -s tests -v

git init
git add .
git commit -m "Initial execution-finality reference implementation"
git branch -M main
git remote add origin <YOUR-GITHUB-REPOSITORY-URL>
git push -u origin main
```

Before the first public push, review `NOTICE.md`, `SECURITY.md`, the IETF IPR disclosure status, and whether a separate software license is intended. No patent license is implied by this archive.

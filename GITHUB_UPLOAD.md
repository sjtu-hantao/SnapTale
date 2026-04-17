# GitHub Upload Notes

This project has now been flattened into a single repository for portfolio-friendly publishing.

That means:

- `backend/` is tracked as a normal directory
- `frontend/` is tracked as a normal directory
- `firmware/` is tracked as a normal directory
- there are no remaining submodule links in the root repository

## Before You Push

Please check these items first:

1. Do not commit `backend/.env`.
2. Make sure no API key appears in tracked files or screenshots.
3. Consider rotating any key that has been shared during development.
4. Decide whether you want to keep `firmware/` in the public repo.

Local-only paths that should stay ignored:

- `backend/.env`
- `backend/storage/`
- `backend/pydeps/`
- `frontend/node_modules/`
- `frontend/build/`

## Recommended Publish Flow

1. Create a new empty GitHub repository under your account.
2. Add it as the `origin` remote for this local repo.
3. Commit the current monorepo structure.
4. Push the default branch.

Example:

```bash
git remote remove origin
git remote add origin https://github.com/<your-name>/<your-repo>.git
git add .
git commit -m "Initial import of SnapTale social storytelling MVP"
git push -u origin main
```

If your default branch is still `master`, replace `main` accordingly.

## Suggested Final Check

Before pushing, run:

```bash
git status
git diff --staged --name-only
```

Make sure the staged changes contain your source code and docs, but not secrets or local runtime data.

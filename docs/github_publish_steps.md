# GitHub Publish Steps

The local git repository is already initialized.

## Suggested repository settings

- Owner: `anasalsharif`
- Name: `optimization-project`
- Visibility: `Public`

## Manual GitHub step

Because GitHub CLI and repo-creation auth are not available in this workspace, create the empty public repository in the browser:

1. Go to `https://github.com/new`
2. Set owner to `anasalsharif`
3. Set repository name to `optimization-project`
4. Choose `Public`
5. Do **not** initialize with README, `.gitignore`, or license
6. Click `Create repository`

## Local push commands

After the repo exists, run:

```powershell
git add .
git commit -m "Initial project setup"
git remote add origin https://github.com/anasalsharif/optimization-project.git
git push -u origin main
```

If `origin` already exists, use:

```powershell
git remote set-url origin https://github.com/anasalsharif/optimization-project.git
git push -u origin main
```

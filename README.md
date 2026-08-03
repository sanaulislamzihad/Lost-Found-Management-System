# CSE327 Project — Lost & Found Management System

A web-based platform for reporting lost and found items, managing claims, and
supporting security verification for campus communities. Built with **Python /
Django** using the **MVT (Model–View–Template)** architectural pattern.

**Course:** Software Engineering (CSE-327)

### Team
- Md Sanaul Islam Zihad
- Shahed Mehbub Shourov
- Jannatun Ferdousi
- Natasha Anwar
- Ridita Rahman

---

## Documentation (GitHub Wiki)

All project documentation lives in the **[GitHub Wiki](https://github.com/sanaulislamzihad/Cse327_project/wiki)**.
A local copy is checked out in the [wiki_repo/](wiki_repo/) folder. Contents:

| Page | What it covers |
|---|---|
| **Home** | Wiki landing page and project overview |
| **SRS** | Software Requirements Specification — full requirements of the system |
| **Architectural Pattern** | Why we chose Django's MVT pattern and how it maps to our system |
| **Coding Standard** | The coding conventions the team follows |
| **Documentation Tool: Sphinx** | How we generate docs with Sphinx |
| **Meeting Agenda 1** | Agenda for the first team meeting |
| **Meeting Minutes 1** | Decisions & action items (Python + Django selected) |

---

## Git Workflow — Commands

> **Note:** This repo has **two** remotes:
> - `origin` → the main code repository
> - `wiki`   → the GitHub Wiki repository
>
> Check them anytime with: `git remote -v`

### 1. Push changes to the main repo

```bash
# Clone the repo (first time only)
git clone https://github.com/sanaulislamzihad/Cse327_project.git
cd Cse327_project

# After making changes:
git status                       # see what has changed
git add .                        # stage all changes
git commit -m "Your message"     # commit
git pull origin main             # pull latest changes first
git push origin main             # push
```

### 2. Create a branch and push it

Always work on a **new branch** instead of directly on `main`.

```bash
git checkout -b feature/my-feature   # create a new branch + switch to it
# ... make your code changes ...
git add .
git commit -m "Add my feature"
git push -u origin feature/my-feature   # first push of the branch (-u sets upstream)
```

Later pushes on the same branch just need: `git push`

### 3. Open a Pull Request (PR)

A PR is how you merge your branch into `main` after review.

**Option A — GitHub website (easiest):**
1. Push your branch (step 2 above).
2. Go to the repo on GitHub → you'll see a **"Compare & pull request"** button → click it.
3. Set **base:** `main` and **compare:** `feature/my-feature`.
4. Write a title + description → click **Create pull request**.
5. Teammates review → then **Merge pull request**.

**Option B — GitHub CLI (`gh`):**
```bash
gh pr create --base main --head feature/my-feature --title "My feature" --body "What this does"
gh pr view --web     # open the PR in the browser
```

After the PR is merged, sync your local `main`:
```bash
git checkout main
git pull origin main
git branch -d feature/my-feature   # delete the old branch (optional)
```

### 4. Push to the GitHub Wiki

The wiki is a separate Git repo. It's already cloned in `wiki_repo/`.

```bash
cd wiki_repo

# To add a new page: create a .md file (e.g. New-Page.md)
# Use hyphens instead of spaces in the name → shows as "New Page".

git add .
git commit -m "Update wiki: New Page"
git pull origin master           # wiki default branch is 'master'
git push origin master           # push to the wiki
```

> **Important:** The Wiki repo's default branch is **`master`** (not `main`).
> After pushing, the changes appear on the GitHub Wiki automatically.

**First time wiki clone (if `wiki_repo/` missing):**
```bash
git clone https://github.com/sanaulislamzihad/Cse327_project.wiki.git wiki_repo
```

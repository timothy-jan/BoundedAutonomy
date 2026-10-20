# Contributing

Every change goes through a pull request so the team can see it and Timothy can review it before it reaches `main`.

## First time

```
git clone https://github.com/timothy-jan/BoundedAutonomy.git
cd BoundedAutonomy
```

## Each change

```
git checkout main
git pull
git checkout -b <your-letter>/<short-name>      # e.g. a/paraphrase-check
# edit files
git add <files>
git commit -m "Short description of the change"
git push -u origin <your-letter>/<short-name>
```

Then open the pull request on GitHub (the push prints a link). Fill in the template. Timothy merges it.

On the website instead: open the file, click the pencil icon, edit, choose "Create a new branch for this commit and start a pull request".

## Rules

- Do not push directly to `main`. GitHub cannot enforce this on a free private repository, so it is a team rule.
- Pull `main` before you start, to avoid conflicts in `tasks/tasks.csv`.
- Keep one topic per pull request.
- Never commit API keys or anything under `runs/`.

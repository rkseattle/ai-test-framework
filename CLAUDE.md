# Setup

After cloning, configure git to use the shared hooks:

```sh
git config core.hooksPath .githooks
```

This enables the pre-commit hook that runs `ruff check` before every commit.

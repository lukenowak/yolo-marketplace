---
name: setup
description: >
  Set up repo-ops on this machine: record the arena repo, the original repo, the
  document space and their tokens. Use when ~/.claude/repo.json is missing or
  incomplete, or when the user hands over a repository, a token, or a document space.
---

# repo-ops setup

The user provides repositories, tokens and a document space; you turn them into
configuration. Report what you set up, never token values.

## Tokens

1. Store each token in `~/.claude/repo_tokens.json` as `{"<key>": {"token": "..."}}`,
   readable only by the owner. Pick descriptive keys, e.g. `<repo>_rw`, `<repo>_ro`.
   Other credentials of a service (a username) go in the same entry.
2. If a token arrives as a link (an encrypted paste, for example), fetch and decrypt it
   locally, show it only masked, and delete every temporary copy afterwards.
3. Verify each token against its repository before relying on it. The arena token must
   be able to push; originals need read access only.

## Configuration

Write `~/.claude/repo.json` (outside the plugin, so plugin updates keep it), following
`repo.json.example` at the plugin root. Leave out keys the user didn't provide.

- `arena_url`, `arena_token_key`: the repository you push task branches to, and the key
  of its write token.
- `originals`: the repositories task branches are cut from, if the user named any, as
  `{"<repo>": {"url": ..., "token_key": ...}}`. `<repo>` is the URL's last path
  component without `.git`; it is the branch component that selects the original, so
  it holds no `/`, no `..` and no leading `-`. Leave out `token_key` for a public
  original. A single original may instead be recorded as `original_url`, shorthand for
  a one-entry `originals` keyed the same way.
- `docs_space` (`kind`, `url`, `token_key`): where you share documents, if provided.

## Arena

- If the arena has no refs, push a branch `no-main` holding only a one-line README; on
  most hosts the first pushed branch becomes the default. If it didn't, ask the user to
  make `no-main` the default branch.
- If the arena already has refs, never re-seed it and never delete branches to make it
  look empty.

## Git

- Clone the arena under `<home>/tmp`; add each original as a remote named `<repo>`.
- Keep tokens out of remote URLs: configure a credential helper that reads
  `~/.claude/repo_tokens.json` and picks the token by repository URL, so each original
  gets its own. URLs with tokens end up in configuration files.
- If git has no global `user.name`/`user.email`, ask the user for the identity to
  commit with.

# repo-ops rules

## Conduct

- Ask before installing a system package or expanding scope. Fixing failures of your
  own task branch, CI failures included, is within scope.
- Share documents in the space named by `docs_space` in `~/.claude/repo.json`. If it
  is unset, ask the user to provide one (for example a SilverBullet space or a Google
  Docs folder) and the access it needs, then record it there, with its credentials in
  `~/.claude/repo_tokens.json`; until then, report in the conversation.
- Follow TDD: write a failing regression test first, then implement. Use synthetic test
  data; mock external processes with the language's standard mocking library rather
  than hand-written fakes.

## Writing style

- Terse commit subjects stating the reason, not a diff summary; never `Co-Authored-By`/
  AI trailers, media, copyrighted content, or binaries.
- Keep one functionality per commit unless coupled tests prove separation impossible.
- Comment on why, not what. Minimal docstrings, minimal comments, no rhetoric,
  self-praise, or narration.
- Commit messages and code comments must not name internal tooling or rule files --
  state only the durable technical reason.

## Arena

- If `~/.claude/repo.json` is missing or incomplete, or the user hands over a
  repository, token or document space, use the `repo-ops:setup` skill.
- Arena (`repo.json`'s `arena_url`) is the one repo an automated session pushes work
  to. Push task branches there, under a namespace prefix that keeps branches
  collision-free when arena is shared across several consumers.
- Arena's default branch carries no content; never push work to it or delete it.
- If `repo.json` names `originals` (or the one-entry shorthand `original_url`), cut
  task branches of `<repo>` from that original's default branch.

## Credentials

- Read tokens from `~/.claude/repo_tokens.json`; never reveal token values -- mask
  them in command output.
- Keep machine-local secrets out of repositories, public text, and session documents;
  anonymize usernames, paths, and hostnames in public text.
- A missing token for a repo `repo.json` newly references is expected until handed
  over directly; ask for it in one line and continue once given.
- Use a write-scoped token for arena. Reading an original only ever needs a read-only
  token.

## Session hygiene

- Develop only in `clone_dir` from `repo.json` (default `<home>/tmp/{repo}`); other
  trees on the host may be read-only references.
- Scratch work goes under `<home>/tmp`, never a shared `/tmp`.
- Keep the shell's working directory at `<home>`: reach other trees with absolute
  paths, `git -C <dir>`, or a `( cd <dir> && ... )` subshell. Deleting the working
  directory or its ancestor asks for confirmation even with permission prompts off.

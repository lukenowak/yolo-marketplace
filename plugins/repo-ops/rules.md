# repo-ops rules

## Conduct

- Install the system packages a task needs without asking; the host is disposable
  and isolated, so its safety comes from that environment, not from prompts. The
  same holds for the rest of the environment -- tool builds, test accounts' local
  setup, keys and credential stores, config: when something is missing, find,
  download or build it yourself. Ask only for what exists solely with the user,
  such as account passwords or tokens not yet handed over.
- Ask before expanding scope. Fixing failures of your own task branch, CI failures
  included, is within scope.
- Share documents in the space named by `docs_space` in `~/.claude/repo.json`. If it
  is unset, ask the user to provide one (for example a SilverBullet space or a Google
  Docs folder) and the access it needs, then record it there, with its credentials in
  `~/.claude/repo_tokens.json`; until then, report in the conversation.
- When `docs_space` has a `publish_command`, publish through `docs_space.publish_command`:
  run it with `{file}` and `{title}` replaced, and hand over the URL it prints. A
  non-zero exit is a failed publish; report it rather than retrying another way, since
  the command owns how documents reach the space. Without the command, publish to the
  space by your own means.
- Follow TDD: write a failing regression test first, then implement. Use synthetic test
  data; mock external processes with the language's standard mocking library rather
  than hand-written fakes.

## Writing style

- Aim for a commit message of one terse line stating the reason, since the diff
  already shows what changed; add a terse explanation below it only when the change
  is too complex for one line.
- Commits hold text you wrote: leave out `Co-Authored-By`/AI trailers, media,
  copyrighted content and binaries, so authorship stays with the committer and every
  change can be reviewed as a diff.
- Keep one functionality per commit unless coupled tests prove separation impossible.
- Give every external reference its full URL at least once in the same message, so
  it can be opened without searching.
- Lead with the conclusion; leave out preamble, restating the request, and summaries
  of what was just done.
- Report times in `timezone` from `repo.json` (the system zone if unset), converted
  and unlabeled; label only a deliberately foreign zone.
- Comment on why, not what. Keep docstrings and comments minimal and factual, without
  rhetoric, self-praise or narration.
- Commit messages and code comments must not name internal tooling or rule files --
  state only the durable technical reason.

## Arena

- If `~/.claude/repo.json` is missing or incomplete, or the user hands over a
  repository, token or document space, use the `repo-ops:setup` skill.
- Arena (`repo.json`'s `arena_url`) is the one repo an automated session pushes work
  to. Push task branches there, under a namespace prefix that keeps branches
  collision-free when arena is shared across several consumers.
- Arena's default branch carries no content; never push work to it or delete it --
  push work to task branches instead.
- If `repo.json` names `originals` (or the one-entry shorthand `original_url`), cut
  task branches of `<repo>` from that original's default branch.

## Development loop

- If the push starts no CI run, the local test run is the verdict; say so when
  reporting.
- After a push, arm a scheduled self-wakeup that checks CI until it reaches a verdict;
  re-arm it at session start while a verdict is still pending. The agent waits for CI
  itself, so never ask the user to check back later.
- A failure is fixed unless it is *pre-existing* (the same failure in a run without the
  change; cite both run URLs) or *infrastructure* (the run broke and tested nothing).
  "flake" is not a verdict; name one of those two or fix it.
- Escalate to the user after two fix attempts without measurable progress, meaning
  fewer failing tests or a later first failure.

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

# yolo-marketplace

Product-agnostic Claude Code marketplace: repo/session tooling with no
product-specific rules baked in.

Install alongside a product marketplace. Supported development hosts are Linux and
Windows.

## Reason

Running an agent is YOLO. Dangerous, yes -- I don't trust agent-written code to be
safe.

Safety and access control belong to the environment, not the agent: OS-level user
separation, jails/containers/VMs, network firewalls, fine-grained per-service tokens,
and disposable/forkable repositories already exist for this. Give the agent freedom
to work; if it escapes, that's an infrastructure gap to fix, not a reason to hold the
agent back.

I treat [agents as subcontractors](https://karavox.org/devlog/agents-as-subcontractors.html)
-- I wouldn't give an external subcontractor my own machine and my own user
privileges, so I don't give one to an agent either. Proper, separated infrastructure
instead.

That's why yolo-marketplace.

## Use with Claude Code

### Install Claude Code

Linux, macOS, WSL:

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

Windows PowerShell:

```powershell
irm https://claude.ai/install.ps1 | iex
```

Other methods are in the [Claude Code setup docs](https://code.claude.com/docs/en/setup).

### Requirements

Install these on the host before installing the plugin:

- `python3` (on Windows, `python` or the `py` launcher also works)
- `curl`

If either is missing, the plugin's hooks stop the session with an error.

### Install the plugin

> [!WARNING]
> Installs into your user settings and turns off Claude Code's permission prompts.
> Only use it in a disposable, isolated environment.
>
> It's really YOLO.

Add the marketplace:

```bash
claude plugin marketplace add https://github.com/lukenowak/yolo-marketplace
```

Install the plugin:

```bash
claude plugin install repo-ops@yolo-marketplace
```

### Update

Update the marketplace & plugin:

```bash
claude plugin marketplace update yolo-marketplace && claude plugin update repo-ops@yolo-marketplace
```

In an already running session, restart it after installation or update -- don't rely on
`/reload-plugins`.

## What to give the agent

Prepare these, then hand them to Claude in a session -- it records them itself:

- **Arena**: an empty repository the agent may write to and destroy, plus a write
  token scoped to just that repository. The agent keeps its default branch empty and
  pushes work to task branches.
- **Original repository** (optional): the repository task branches are cut from, plus
  a read-only token if it is private.
- **Document space** (optional): somewhere the agent can share documents, e.g. a
  SilverBullet space or a Google Docs folder, plus access to it. Without one, the agent
  asks when it first needs it.

For example: "Work on `<original repo URL>` in `<arena repo URL>`; tokens are in
`<link>`."

## Validating

```bash
claude plugin validate ./plugins/repo-ops
python3 -m unittest discover -s tests
```

## License

GPL-3.0-or-later. See `LICENSE`.

# herdr-sort-spaces

A [Herdr](https://herdr.dev) plugin that keeps your **spaces** (workspaces) sorted by title.
A space's title is its directory name unless you renamed it. Sorting is case-insensitive, and a
space is moved together with the linked-worktree spaces that follow it.

It is event-driven: you do not have to press anything.

| Trigger | Why |
|---|---|
| session startup | initial sort |
| `workspace.created` | a new space lands in its sorted place |
| `workspace.renamed` | a renamed space moves to its new place |
| action `sort` | on demand (command palette or a keybind) |

`workspace.moved` / `workspace.reordered` are deliberately **not** hooked, so the plugin never
re-triggers itself. The script is idempotent and makes no API call when already sorted.

## Install

```sh
herdr plugin install SeitaHigashi/herdr-sort-spaces --yes
```

Local checkout instead:

```sh
herdr plugin link /path/to/herdr-sort-spaces
```

Requires `python3` (standard library only) and Herdr >= 0.9.0.
On NixOS / Nix, see [Nix](#nix) below.

## Keybind (optional)

Add to `config.toml`, then run `herdr server reload-config`:

```toml
[[keys.command]]
key = "prefix+s"
type = "plugin_action"
command = "seitahigashi.herdr-sort-spaces.sort"
description = "sort spaces"
```

Without the `prefix+`, a key such as `ctrl+alt+s` is a direct shortcut.
Run `herdr config check` after editing; avoid keys already used by Herdr's built-in bindings.

The action can also be run from the shell:

```sh
herdr plugin action invoke seitahigashi.herdr-sort-spaces.sort
```

## Limitations

- **`cd` does not re-sort.** `cd` inside a pane changes the space's title, but Herdr emits no event for
  it (checked against every hookable and subscribable event), so the order is refreshed on the next
  create / rename or when you run the `sort` action. To refresh on every `cd`, run the action above from
  your shell's `chpwd` hook (zsh) or `PROMPT_COMMAND` (bash) — not provided or tested here.
- A manual drag in the sidebar stays until the next trigger.
- Order is plain case-insensitive string order, so a space titled `~` sorts last.
- Sort key and order are not configurable yet.

## Development

```sh
python3 test_sort_spaces.py     # pure planning logic, no Herdr needed
herdr plugin link "$PWD"         # try it against a running session (absolute path)
```

Try it without touching your live session by starting a separate one
(`herdr --session sorttest`) and pointing `HERDR_SOCKET_PATH` at
`~/.config/herdr/sessions/sorttest/herdr.sock`.

## Nix

Everything above works on Nix systems as long as `python3` is on the PATH that **Herdr** runs plugin
commands with, which on NixOS is often not the case. The flake builds the plugin directory with
`python3` pinned to a store path, so it does not depend on `PATH`. Its layout follows
[Herdr's own flake](https://github.com/herdrdev/herdr/blob/HEAD/flake.nix): `nixpkgs-unstable`, the same
four systems, `packages.default` and `checks`.

```sh
# Build, keeping a GC root so the store path stays alive, then link it.
nix build github:SeitaHigashi/herdr-sort-spaces -o ~/.local/share/herdr-sort-spaces
herdr plugin link ~/.local/share/herdr-sort-spaces
```

As a flake input (so `nix flake update herdr-sort-spaces` updates it):

```nix
inputs.herdr-sort-spaces.url = "github:SeitaHigashi/herdr-sort-spaces";
# ... then link  inputs.herdr-sort-spaces.packages.${system}.default
```

Notes:

- Herdr's plugin registry is runtime state (`herdr plugin link` writes it), not declarative. After a
  rebuild that changes the store path, run `herdr plugin link` again on the new path.
- `nix flake check` runs the unit test.
- The Nix package does not need `[[build]]`; there is nothing to compile.

## License

MIT

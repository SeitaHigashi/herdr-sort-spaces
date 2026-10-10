#!/usr/bin/env python3
"""Sort Herdr spaces (workspaces) by title. Idempotent: does nothing when already sorted."""
import json
import os
import socket
import sys


def call(method, **params):
    s = socket.socket(socket.AF_UNIX)
    s.settimeout(5)
    s.connect(os.environ["HERDR_SOCKET_PATH"])
    s.sendall((json.dumps({"id": "sort-spaces", "method": method, "params": params}) + "\n").encode())
    resp = json.loads(s.makefile().readline())
    s.close()
    if "error" in resp:
        sys.exit(f"sort-spaces: {method}: {resp['error']}")
    return resp["result"]


def units(workspaces):
    """Group the flat sidebar order into blocks: a space plus the linked worktree spaces under it."""
    out = []
    for w in workspaces:
        wt = w.get("worktree") or {}
        parent = out[-1] if out else None
        if wt.get("is_linked_worktree") and parent and (parent[0].get("worktree") or {}).get("repo_key") == wt.get("repo_key"):
            parent.append(w)
        else:
            out.append([w])
    return out


def plan(workspaces):
    """Return the [(workspace_ids, before_workspace_id)] moves that sort the sidebar; [] if already sorted."""
    desired = sorted(units(workspaces), key=lambda u: (u[0]["label"].casefold(), u[0]["workspace_id"]))
    ids = [w["workspace_id"] for w in workspaces]
    moves = []
    # Walk backwards: put each block directly before the block that must follow it (last block -> end).
    nxt = None
    for u in reversed(desired):
        block = [w["workspace_id"] for w in u]
        end = ids.index(block[-1])
        after = ids[end + 1] if end + 1 < len(ids) else None
        if after != nxt:
            moves.append((block, nxt))
            ids = [i for i in ids if i not in block]
            at = ids.index(nxt) if nxt else len(ids)
            ids[at:at] = block
        nxt = block[0]
    return moves


def main():
    for block, before in plan(call("workspace.list")["workspaces"]):
        call("workspace.move_block", workspace_ids=block, before_workspace_id=before)


if __name__ == "__main__":
    main()

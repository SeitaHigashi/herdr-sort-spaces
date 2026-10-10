#!/usr/bin/env python3
"""Self-check for the planning logic: python3 test_sort_spaces.py (no Herdr needed)."""
from sort_spaces import plan


def ws(i, label, repo=None, linked=False):
    w = {"workspace_id": i, "label": label}
    if repo:
        w["worktree"] = {"repo_key": repo, "is_linked_worktree": linked}
    return w


def apply(workspaces, moves):
    """Replay moves the way Herdr's workspace.move_block would, returning the resulting id order."""
    ids = [w["workspace_id"] for w in workspaces]
    for block, before in moves:
        ids = [i for i in ids if i not in block]
        at = ids.index(before) if before else len(ids)
        ids[at:at] = block
    return ids


def check(workspaces, expected):
    assert apply(workspaces, plan(workspaces)) == expected, (plan(workspaces), expected)
    sorted_ws = sorted(workspaces, key=lambda w: expected.index(w["workspace_id"]))
    assert plan(sorted_ws) == [], "second pass must be a no-op"


# plain spaces: case-insensitive, stable on ties
check([ws("w1", "zeta"), ws("w2", "Alpha"), ws("w3", "mid")], ["w2", "w3", "w1"])
check([ws("w1", "b"), ws("w2", "B")], ["w1", "w2"])
# already sorted -> no moves
assert plan([ws("w1", "a"), ws("w2", "b")]) == []
# linked worktree spaces travel with their parent block
check(
    [ws("w1", "zeta"), ws("w2", "repo", "R"), ws("w3", "repo-feat", "R", True), ws("w4", "alpha")],
    ["w4", "w2", "w3", "w1"],
)
print("ok")

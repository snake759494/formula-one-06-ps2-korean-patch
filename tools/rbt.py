# Serialized red-black tree used by F1 06 (.bft fonts, .blf text).
# Nodes 0 and 1 are sentinels; keyed nodes are 2..n+1 in sorted key order.
# Tail of every node (7 i32): [next][prev][idx][left][right][parent][black]  (relative indices; nil = node 0)
# Shape = sorted keys inserted one by one into a classic RB tree.

def build(n):
    """returns dict k -> (left, right, parent, black) absolute indices for k in 2..n+1, and root."""
    NIL = 0
    L = {}; R = {}; P = {}; B = {}
    root = NIL
    def rot_l(x):
        nonlocal root
        y = R[x]; R[x] = L[y]
        if L[y] != NIL: P[L[y]] = x
        P[y] = P[x]
        if P[x] == NIL: root = y
        elif x == L[P[x]]: L[P[x]] = y
        else: R[P[x]] = y
        L[y] = x; P[x] = y
    def rot_r(x):
        nonlocal root
        y = L[x]; L[x] = R[y]
        if R[y] != NIL: P[R[y]] = x
        P[y] = P[x]
        if P[x] == NIL: root = y
        elif x == R[P[x]]: R[P[x]] = y
        else: L[P[x]] = y
        R[y] = x; P[x] = y
    last = NIL
    for z in range(2, n + 2):
        # sorted insert: z goes to the right of the current maximum
        L[z] = R[z] = NIL; B[z] = 0
        if root == NIL:
            root = z; P[z] = NIL
        else:
            y = root
            while R[y] != NIL: y = R[y]
            R[y] = z; P[z] = y
        while P[z] != NIL and B[P[z]] == 0:
            g = P[P[z]]
            if P[z] == L.get(g):
                u = R[g]
                if u != NIL and B[u] == 0:
                    B[P[z]] = 1; B[u] = 1; B[g] = 0; z = g
                else:
                    if z == R[P[z]]: z = P[z]; rot_l(z)
                    B[P[z]] = 1; B[g] = 0; rot_r(g)
            else:
                u = L[g]
                if u != NIL and B[u] == 0:
                    B[P[z]] = 1; B[u] = 1; B[g] = 0; z = g
                else:
                    if z == L[P[z]]: z = P[z]; rot_r(z)
                    B[P[z]] = 1; B[g] = 0; rot_l(g)
        B[root] = 1
    return {k: (L[k], R[k], P[k], B[k]) for k in range(2, n + 2)}, root

def tails(n):
    t, root = build(n)
    out = {}
    for k in range(2, n + 2):
        l, r, p, b = t[k]
        nxt = 1 if k < n + 1 else 0
        prv = -1 if k > 2 else 0
        out[k] = (nxt, prv, k, l - k, r - k, (p if p else k) - k, b)
    return out, root

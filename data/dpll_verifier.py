"""Self-contained DPLL solver and puzzle verifier."""
import itertools
from Source.engine.region_helper import RegionHelper

def fast_dpll(clauses: list[list[int]], assignment: dict[int, bool] = None) -> tuple[bool, dict[int, bool] | None]:
    """Pure-Python DPLL solver with unit propagation and backtracking."""
    if assignment is None:
        assignment = {}
    else:
        assignment = dict(assignment)

    # Unit propagation
    changed = True
    while changed:
        changed = False
        unit_lit = None
        for c in clauses:
            unassigned = []
            satisfied = False
            for lit in c:
                var = abs(lit)
                val = (lit > 0)
                if var in assignment:
                    if assignment[var] == val:
                        satisfied = True
                        break
                else:
                    unassigned.append(lit)
            if satisfied:
                continue
            if len(unassigned) == 0:
                return False, None
            if len(unassigned) == 1:
                unit_lit = unassigned[0]
                break

        if unit_lit is not None:
            var = abs(unit_lit)
            val = (unit_lit > 0)
            if var in assignment and assignment[var] != val:
                return False, None
            assignment[var] = val
            changed = True

    # Check if all clauses satisfied
    all_satisfied = True
    for c in clauses:
        if not any(assignment.get(abs(lit)) == (lit > 0) for lit in c):
            all_satisfied = False
            break
    if all_satisfied:
        return True, assignment

    # Branching
    all_vars = {abs(lit) for c in clauses for lit in c}
    unassigned_vars = [v for v in sorted(all_vars) if v not in assignment]
    if not unassigned_vars:
        return False, None

    var = unassigned_vars[0]
    # Try True
    sat, m = fast_dpll(clauses, {**assignment, var: True})
    if sat:
        return True, m
    # Try False
    return fast_dpll(clauses, {**assignment, var: False})

def encode_clue_to_cnf(clue: dict, var_map: dict[str, int], size: int) -> list[list[int]]:
    ctype = clue["type"]
    params = clue.get("params", {})
    clauses = []

    if ctype == "FACT":
        v = var_map[params["target"]]
        clauses.append([v] if params["status"] == "CRIMINAL" else [-v])

    elif ctype == "SAME":
        v1 = var_map[params["target1"]]
        v2 = var_map[params["target2"]]
        clauses.append([-v1, v2])
        clauses.append([v1, -v2])

    elif ctype == "DIFFERENT":
        v1 = var_map[params["target1"]]
        v2 = var_map[params["target2"]]
        clauses.append([v1, v2])
        clauses.append([-v1, -v2])

    elif ctype in ("EXACTLY", "AT_LEAST", "AT_MOST"):
        cells = RegionHelper.resolve_region(params["region"], size)
        vars_ = [var_map[c] for c in cells]
        m = len(vars_)
        k = params["count"]

        if ctype in ("EXACTLY", "AT_LEAST"):
            if k > m:
                clauses.append([])
            elif k > 0:
                for comb in itertools.combinations(vars_, m - k + 1):
                    clauses.append(list(comb))

        if ctype in ("EXACTLY", "AT_MOST"):
            if k < m:
                for comb in itertools.combinations(vars_, k + 1):
                    clauses.append([-v for v in comb])

    elif ctype == "PARITY":
        cells = RegionHelper.resolve_region(params["region"], size)
        vars_ = [var_map[c] for c in cells]
        target_even = (params["parity"] == "EVEN")
        for bits in itertools.product([0, 1], repeat=len(vars_)):
            is_even = (sum(bits) % 2 == 0)
            if is_even != target_even:
                clause = [(-vars_[i] if bits[i] == 1 else vars_[i]) for i in range(len(vars_))]
                clauses.append(clause)

    elif ctype == "COUNT_COMPARE":
        r1 = RegionHelper.resolve_region(params["region1"], size)
        r2 = RegionHelper.resolve_region(params["region2"], size)
        all_r = list(dict.fromkeys(r1 + r2))
        op = params["operator"]
        
        for bits in itertools.product([0, 1], repeat=len(all_r)):
            assign = dict(zip(all_r, bits))
            c1 = sum(assign[c] for c in r1)
            c2 = sum(assign[c] for c in r2)
            valid = False
            if op == "GT": valid = (c1 > c2)
            elif op == "GTE": valid = (c1 >= c2)
            elif op == "LT": valid = (c1 < c2)
            elif op == "LTE": valid = (c1 <= c2)
            elif op == "EQ": valid = (c1 == c2)
            
            if not valid:
                clause = [(-var_map[all_r[i]] if bits[i] == 1 else var_map[all_r[i]]) for i in range(len(all_r))]
                clauses.append(clause)

    return clauses

def verify_puzzle_with_dpll(puzzle_data: dict) -> bool:
    size = puzzle_data["size"]
    grid = puzzle_data["grid"]
    all_cells = [c["id"] for c in grid]
    var_map = {c: i + 1 for i, c in enumerate(all_cells)}
    gt = {c["id"]: (c["hidden_status"] == "CRIMINAL") for c in grid}
    all_clues = {c["id"]: c["clue"] for c in grid}

    print(f"\n=======================================================")
    print(f"VERIFYING: {puzzle_data['puzzle_id']} — {puzzle_data['name']} ({size}x{size})")
    print(f"=======================================================")

    all_clauses = []
    for cid, clue in all_clues.items():
        cls = encode_clue_to_cnf(clue, var_map, size)
        all_clauses.extend(cls)

    # 1. Ground truth consistency
    gt_model = {var_map[c]: gt[c] for c in all_cells}
    for clause in all_clauses:
        if not any(gt_model[abs(lit)] == (lit > 0) for lit in clause):
            print(f"❌ Ground truth violates clause: {clause}")
            return False
    print("✅ Ground truth satisfies 100% of CNF clauses.")

    # 2. Check Uniqueness
    is_sat, model = fast_dpll(all_clauses)
    if not is_sat:
        print("❌ Full formula is UNSAT!")
        return False

    blocking_clause = [-var_map[c] if gt[c] else var_map[c] for c in all_cells]
    is_sat2, model2 = fast_dpll(all_clauses + [blocking_clause])
    if is_sat2:
        print("❌ Multiple solutions exist! Not unique!")
        return False
    print("✅ Uniqueness proven: Exactly 1 satisfying solution exists!")

    # 3. Simulate No-Guess Deduction Loop step-by-step
    revealed = set(puzzle_data.get("initial_revealed", []))
    active_clues = [all_clues[cid] for cid in revealed]
    step = 0

    while len(revealed) < len(all_cells):
        step += 1
        unsolved = [c for c in all_cells if c not in revealed]

        kb_clauses = []
        for cl in active_clues:
            kb_clauses.extend(encode_clue_to_cnf(cl, var_map, size))
        for rc in revealed:
            v = var_map[rc]
            kb_clauses.append([v] if gt[rc] else [-v])

        forced = []
        for candidate in unsolved:
            v = var_map[candidate]
            # Test candidate == CRIMINAL
            is_sat_neg, _ = fast_dpll(kb_clauses + [[-v]])
            if not is_sat_neg:
                forced.append((candidate, "CRIMINAL"))
                continue

            # Test candidate == INNOCENT
            is_sat_pos, _ = fast_dpll(kb_clauses + [[v]])
            if not is_sat_pos:
                forced.append((candidate, "INNOCENT"))
                continue

        if not forced:
            print(f"❌ Deadlock at step {step}! Unsolved: {unsolved}")
            return False

        next_cell, verdict = forced[0]
        expected_verdict = "CRIMINAL" if gt[next_cell] else "INNOCENT"
        assert verdict == expected_verdict

        print(f"Step {step:02d}: Cell {next_cell} forced to {verdict:<8} (Wave forced count: {len(forced)})")
        revealed.add(next_cell)
        active_clues.append(all_clues[next_cell])

    print(f"✅ PUZZLE {puzzle_data['puzzle_id']} IS 100% NO-GUESS SOLVABLE IN {step} STEPS!\n")
    return True

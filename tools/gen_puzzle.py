import json, itertools, random, sys
N=3; CELLS=[f"{chr(65+c)}{r+1}" for r in range(N) for c in range(N)]
def region(r):
    t=r["type"]
    if t=="ROW": return [f"{chr(65+c)}{r['row']}" for c in range(N)]
    if t=="COLUMN": return [f"{r['col']}{i}" for i in range(1,N+1)]
    if t=="EXPLICIT": return list(r["cells"])
    col=ord(r["cell"][0])-65; row=int(r["cell"][1:])-1
    return [f"{chr(65+col+dc)}{row+dr+1}" for dr in (-1,0,1) for dc in (-1,0,1) if (dr,dc)!=(0,0) and 0<=row+dr<N and 0<=col+dc<N]
def ev(cl,a):
    t,p=cl["type"],cl["params"]
    if t=="FACT": return a[p["target"]]==(p["status"]=="CRIMINAL")
    if t=="SAME": return a[p["target1"]]==a[p["target2"]]
    if t=="DIFFERENT": return a[p["target1"]]!=a[p["target2"]]
    if t in("EXACTLY","AT_LEAST","AT_MOST"):
        n=sum(a[c] for c in region(p["region"])); k=p["count"]
        return n==k if t=="EXACTLY" else n>=k if t=="AT_LEAST" else n<=k
    if t=="PARITY": return sum(a[c] for c in region(p["region"]))%2==(0 if p["parity"]=="EVEN" else 1)
    x=sum(a[c] for c in region(p["region1"])); y=sum(a[c] for c in region(p["region2"]))
    return {"GT":x>y,"GTE":x>=y,"LT":x<y,"LTE":x<=y,"EQ":x==y}[p["operator"]]
def rnd_region(rng):
    t=rng.choice(["ROW","COLUMN","EXPLICIT","NEIGHBORS"])
    if t=="ROW": return {"type":t,"row":rng.randint(1,N)}
    if t=="COLUMN": return {"type":t,"col":rng.choice("ABC")}
    if t=="NEIGHBORS": return {"type":t,"cell":rng.choice(CELLS)}
    return {"type":t,"cells":sorted(rng.sample(CELLS,rng.randint(2,3)))}
def rnd_clue(rng,sol,cid):
    for _ in range(200):
        t=rng.choice(["FACT","SAME","DIFFERENT","EXACTLY","AT_LEAST","AT_MOST","PARITY","COUNT_COMPARE"])
        if t=="FACT": p={"target":rng.choice(CELLS)}; p["status"]="CRIMINAL" if sol[p["target"]] else "INNOCENT"
        elif t in("SAME","DIFFERENT"): a,b=rng.sample(CELLS,2); p={"target1":a,"target2":b}
        elif t=="PARITY": r=rnd_region(rng); p={"region":r,"parity":"EVEN" if sum(sol[c] for c in region(r))%2==0 else "ODD"}
        elif t=="COUNT_COMPARE": p={"operator":rng.choice(["GT","GTE","LT","LTE","EQ"]),"region1":rnd_region(rng),"region2":rnd_region(rng)}
        else:
            r=rnd_region(rng); n=sum(sol[c] for c in region(r)); p={"count":n,"region":r}
        cl={"id":f"clue_{cid}","type":t,"params":p,"description":f"{t} {json.dumps(p)}"}
        if ev(cl,sol): return cl
def solvable(grid,init):
    revealed=set(init); 
    sol={c["id"]:c["hidden_status"]=="CRIMINAL" for c in grid}
    clues={c["id"]:c["clue"] for c in grid}
    while len(revealed)<len(CELLS):
        models=[dict(zip(CELLS,b)) for b in itertools.product([False,True],repeat=len(CELLS))
                if all(b[CELLS.index(c)]==sol[c] for c in revealed) and all(ev(clues[c],dict(zip(CELLS,b))) for c in revealed)]
        if not models: return False
        forced=[c for c in CELLS if c not in revealed and len({m[c] for m in models})==1]
        if not forced: return False
        revealed.add(forced[0])
    return True
def unique(grid):
    ms=[b for b in itertools.product([False,True],repeat=len(CELLS)) if all(ev(c["clue"],dict(zip(CELLS,b))) for c in grid)]
    return len(ms)==1
seed=int(sys.argv[1]) if len(sys.argv)>1 else 1
rng=random.Random(seed)
for attempt in range(20000):
    sol={c:rng.random()<0.4 for c in CELLS}
    if not 2<=sum(sol.values())<=5: continue
    grid=[{"id":c,"row":int(c[1]),"col":c[0],"character":{"name":n,"occupation":o},
           "hidden_status":"CRIMINAL" if sol[c] else "INNOCENT","clue":rnd_clue(rng,sol,c)}
          for c,(n,o) in zip(CELLS,[("Abel","Baker"),("Bea","Cook"),("Clara","Guard"),("Derek","Cook"),("Eliza","Judge"),("Franz","Clerk"),("Grant","Farmer"),("Hannah","Nurse"),("Ivy","Clerk")])]
    init=[rng.choice(CELLS)]
    if unique(grid) and solvable(grid,init):
        json.dump({"puzzle_id":f"gen_3x3_{seed}","name":f"Generated 3x3 #{seed}","size":3,"initial_revealed":init,"grid":grid},open(f"data/gen_3x3_{seed}.json","w"),indent=2)
        print("ok attempt",attempt,"init",init); break
else: print("no puzzle found")

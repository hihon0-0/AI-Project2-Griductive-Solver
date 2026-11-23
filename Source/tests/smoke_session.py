import sys, traceback
sys.path.insert(0, ".")
from Source.gui.session import GameSession

s = GameSession()
print("warnings:", s.warnings)
s.load(sys.argv[1])
print("warnings after load:", s.warnings)
print("size", s.size, "name", s.name)
print("statuses:", s.statuses())
print("is_solved:", s.is_solved(), "terminal:", s.terminal)
print("clue_of A1:", s.clue_of("A1"))
print("character B2:", s.character("B2"))
print("metrics:", s.metrics())
print("hint:", s.hint())
for i in range(12):
    o = s.next_step()
    print(i, o.kind, o.cell, o.verdict, o.clue_ids)
    if o.kind != "OK": break
print("final terminal:", s.terminal, "solved:", s.is_solved())
print("log:"); [print("  ", r) for r in s.log]
print("metrics:", s.metrics())

import bisect, re, subprocess, sys, collections
import os
O = os.environ.get("OELF", "/home/shiro/dolphinps4-build/build/dolphin/Source/Core/DolphinNoGUI/dolphin-nogui_eboot/dolphin-nogui.oelf")
out = subprocess.run(["llvm-nm-21", "-n", "--demangle", O], capture_output=True, text=True).stdout
syms = []
for line in out.splitlines():
    p = line.split(" ", 2)
    if len(p) == 3 and p[1] in "tTwW" and p[0].strip():
        syms.append((int(p[0], 16), p[2]))
syms.sort()
addrs = [a for a, _ in syms]

def name(v):
    i = bisect.bisect_right(addrs, v) - 1
    return syms[i][1] if i >= 0 else "?"

lo, hi = float(sys.argv[2]), float(sys.argv[3])
totals = collections.defaultdict(lambda: collections.Counter())
windows = collections.Counter()
thread = None
for line in open(sys.argv[1]):
    m = re.match(r"== ([\d.]+) s, (.*?): (\d+) samples", line)
    if m:
        t = float(m.group(1))
        thread = m.group(2) if lo <= t <= hi else None
        if thread:
            windows[thread] += 1
        continue
    if not thread:
        continue
    m = re.match(r"\s+([\d.]+)% (elf|region|syscall from elf) (0x[0-9a-f]+)", line)
    if not m:
        continue
    pct, kind, a = float(m.group(1)), m.group(2), int(m.group(3), 16)
    key = name(a)[:110] if kind == "elf" else ("SYS<- " + name(a)[:100]) if kind.startswith("syscall") else "[%s %#x]" % ("system libs" if a == 0x800000000 else "JIT/other", a)
    totals[thread][key] += pct
for thread, c in totals.items():
    n = windows[thread]
    print("#### %s (%d windows)" % (thread, n))
    for k, v in c.most_common(int(os.environ.get("TOPN","28"))):
        print("  %5.1f%%  %s" % (v / n, k))

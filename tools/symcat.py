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

CATS = [
    ("RADV/Mesa", r"^(radv_|ac_|vk_|util_|nir_|aco|_mesa|ralloc|si_|u_|radeon_|amdgpu_|ps4_scan|ps4_check|ps4_record)"),
    ("Vulkan backend", r"^Vulkan::"),
    ("texture cache/decode", r"TextureCache|TexDecoder|TextureInfo|TMEM|Hash64|GetHash|XXH"),
    ("vertex loading", r"VertexLoader|VertexManager|IndexGenerator|CPState|VertexShaderManager|GeometryShaderManager"),
    ("FIFO/command processing", r"Fifo::|OpcodeDecoder|CommandProcessor|LoadBPReg|LoadXFReg|BPFunctions|XFStruct|ReadDataFromFifo"),
    ("pixel/shader state", r"PixelShaderManager|ShaderCache|ShaderGen|GXPipeline|PipelineConfig|PixelShaderGen|VertexShaderGen|UberShader"),
    ("memory copies", r"^(memcpy|memmove|memset|memcmp|bcmp)$|CopyFromEmu|GetPointerForRange"),
]
lo, hi = float(sys.argv[2]), float(sys.argv[3])
totals = collections.defaultdict(collections.Counter)
other = collections.defaultdict(collections.Counter)
windows = collections.Counter()
thread = None
for line in open(sys.argv[1]):
    m = re.match(r"== ([\d.]+) s, (.*?): (\d+) samples", line)
    if m:
        thread = m.group(2) if lo <= float(m.group(1)) <= hi else None
        if thread:
            windows[thread] += 1
        continue
    if not thread:
        continue
    m = re.match(r"\s+([\d.]+)% (elf|region|syscall from elf) (0x[0-9a-f]+)", line)
    if not m:
        continue
    pct, kind, a = float(m.group(1)), m.group(2), int(m.group(3), 16)
    if kind == "region":
        cat = "system libs (direct)" if a == 0x800000000 else "JIT code / other regions"
        n = cat
    else:
        n = name(a)
        cat = "Dolphin other"
        for c, rx in CATS:
            if re.search(rx, n):
                cat = c
                break
        if kind.startswith("syscall"):
            cat = "system libs <- " + cat
    totals[thread][cat] += pct
    if cat in ("Dolphin other", "RADV/Mesa"):
        other[thread][n[:90]] += pct
for t, c in totals.items():
    n = windows[t]
    print("#### %s (%d windows)" % (t, n))
    for k, v in c.most_common():
        print("  %5.1f%%  %s" % (v / n, k))
    print("  -- top of Dolphin other / RADV:")
    for k, v in other[t].most_common(12):
        print("     %5.1f%%  %s" % (v / n, k))

#!/usr/bin/env python3
"""
Chromaprint Pass — finds which memos are the SAME music (versions/duplicates).

WHAT THIS DOES
  Fingerprints all 916 voice memos with Chromaprint (fpcalc, installed with
  the Workbench) and clusters recordings whose audio actually matches —
  catching version families the titles and transcripts can't see (hummed
  takes of the same melody years apart, retitled duplicates, etc.).
  Writes results to "03 Voice Memos/audio_fingerprint_clusters.json".
  Read-only: originals untouched.

HOW TO RUN (Terminal on the mac mini)
  cd "/Users/jeffstory/Music/Jeff Story Song Vault"
  python3 chromaprint_pass.py

  Takes roughly 15-30 minutes for 916 files; safe to leave running.
  Resumable — rerun anytime, it skips finished fingerprints.
  If it says fpcalc not found, run:  brew install chromaprint
  Tell Claude when it's done — Claude reads the clusters and folds the
  version families into the catalog next session.
"""
import os, sys, json, subprocess, shutil

VAULT = os.path.expanduser("~/Music/Jeff Story Song Vault")
INTAKE = os.path.join(VAULT, "Voice Memo Intake")
OUTDIR = os.path.join(VAULT, "03 Voice Memos")
FP_CACHE = os.path.join(OUTDIR, "_fingerprints.json")
CLUSTERS = os.path.join(OUTDIR, "audio_fingerprint_clusters.json")

def fpcalc_path():
    p = shutil.which("fpcalc")
    if p: return p
    for c in ("/opt/homebrew/bin/fpcalc", "/usr/local/bin/fpcalc"):
        if os.path.exists(c): return c
    return None

def similarity(a, b):
    n = min(len(a), len(b))
    if n < 20: return 0.0
    same = sum(1 for x, y in zip(a[:n], b[:n]) if bin(x ^ y).count("1") <= 6)
    return same / n

def main():
    fp = fpcalc_path()
    if not fp:
        print("ERROR: fpcalc not found. Run:  brew install chromaprint")
        sys.exit(1)

    files = sorted(f for f in os.listdir(INTAKE) if f.lower().endswith(".m4a"))
    cache = {}
    if os.path.exists(FP_CACHE):
        cache = json.load(open(FP_CACHE))

    print(f"Fingerprinting {len(files)} memos ({len(cache)} already cached)...")
    for i, f in enumerate(files, 1):
        if f in cache: continue
        try:
            r = subprocess.run([fp, "-raw", "-length", "120", "-json",
                                os.path.join(INTAKE, f)],
                               capture_output=True, text=True, timeout=60)
            d = json.loads(r.stdout)
            cache[f] = d.get("fingerprint", [])
        except Exception as e:
            cache[f] = []
        if i % 25 == 0:
            json.dump(cache, open(FP_CACHE, "w"))
            print(f"  [{i}/{len(files)}]")
    json.dump(cache, open(FP_CACHE, "w"))

    print("Clustering (this part is quick)...")
    names = [f for f in files if len(cache.get(f, [])) >= 20]
    parent = {f: f for f in names}
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]; x = parent[x]
        return x
    pairs = 0
    for i in range(len(names)):
        fi = cache[names[i]]
        for j in range(i + 1, len(names)):
            # cheap length gate before the expensive compare
            if abs(len(fi) - len(cache[names[j]])) > 0.5 * max(len(fi), len(cache[names[j]])):
                continue
            if similarity(fi, cache[names[j]]) >= 0.55:
                parent[find(names[i])] = find(names[j]); pairs += 1
    groups = {}
    for f in names:
        groups.setdefault(find(f), []).append(f)
    clusters = [sorted(g) for g in groups.values() if len(g) > 1]
    clusters.sort(key=len, reverse=True)
    json.dump({"clusters": clusters, "threshold": 0.55,
               "note": "same-audio families among 916 memos; verify by ear before merging catalog entries"},
              open(CLUSTERS, "w"), indent=1)
    print(f"\nDone: {len(clusters)} version families found ({pairs} matching pairs).")
    print(f"Results: {CLUSTERS}")
    print("Tell Claude it's done — the clusters get folded into the catalog next session.")

if __name__ == "__main__":
    main()

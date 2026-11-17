import json, math, os, glob
from datetime import datetime

def parse_iso(ts): return datetime.fromisoformat(ts.replace('Z', '+00:00'))

def get_h_map(hourly, day_start_dt):
    h_map = {}
    for h_data in hourly:
        t = parse_iso(h_data['from'])
        h = int((t - day_start_dt).total_seconds() // 3600) + 1
        if 1 <= h <= 24: h_map[h] = h_data['viewers']
    return h_map

def get_v1(case):
    known = case.get("known", [])
    if known and known[0].get("viewers", 0) > 0: return known[0]["viewers"]
    all_viewers = []
    for c in case.get("comparables", []):
        h_map = get_h_map(c.get("hourly", []), parse_iso(c['day_start']))
        all_viewers.extend([v for v in h_map.values() if v > 0])
    return sorted(all_viewers)[len(all_viewers)//2] if all_viewers else 1000

def get_ratios(comparables):
    ratios = {}
    for c in comparables:
        h_map = get_h_map(c.get("hourly", []), parse_iso(c['day_start']))
        v1 = h_map.get(1, 0)
        if v1 <= 0: continue
        for h in range(2, 25):
            if h in h_map and h_map[h] > 0:
                ratios.setdefault(h, []).append(math.log(h_map[h] / v1))
    return ratios

def main():
    SIGMA_FLOOR, SPREAD_K, SMOOTHING = 0.5, 0.8, False
    in_dir = os.environ.get("MAKEFUN_INPUT_DIR", "/input")
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    for f in sorted(glob.glob(os.path.join(in_dir, "*.in"))):
        case = json.load(open(f))
        v1 = get_v1(case)
        ratios = get_ratios(case.get("comparables", []))
        m_h = {h: sorted(ratios.get(h, [0]))[len(ratios.get(h, [0]))//2] for h in range(2, 25)}
        if SMOOTHING:
            new_m = {}
            for h in range(2, 25):
                win = [m_h.get(h+d, 0) for d in [-1, 0, 1] if 2 <= h+d <= 24]
                new_m[h] = sum(win)/len(win)
            m_h = new_m
        q15 = {h: sorted(ratios.get(h, [0]))[max(0, int(0.15*len(ratios.get(h, [0]))))] for h in range(2, 25)}
        q85 = {h: sorted(ratios.get(h, [0]))[min(len(ratios.get(h, [0]))-1, int(0.85*len(ratios.get(h, [0]))))] for h in range(2, 25)}
        
        hours_res = []
        for h in range(2, 25):
            med = v1 * math.exp(m_h[h])
            s = max(SIGMA_FLOOR, SPREAD_K * (q85[h] - q15[h]) / 2)
            qs = sorted([max(1, min(1e9, med * math.exp(zv * s))) for zv in [-1.6449, -0.6745, 0.0, 0.6745, 1.6449]])
            hours_res.append({"hour": h, "q": qs})
        json.dump({"hours": hours_res}, open(os.path.join(out_dir, os.path.basename(f).replace('.in', '.out')), 'w'))

if __name__ == "__main__": main()

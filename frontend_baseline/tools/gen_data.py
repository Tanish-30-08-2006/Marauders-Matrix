# Bakes the demo dataset into data.js. Seeded, so output never changes.
import json, random
random.seed(7)
HOSP = [("H1", "Sri Venkat Medical", "Hyderabad"), ("H2", "Kaveri Heart & Critical Care", "Chennai"),
        ("H3", "Deccan Institute of Medicine", "Pune"), ("H4", "Sabarmati General", "Ahmedabad")]
F = "Ananya Lakshmi Meera Priya Kavya Divya Sneha Pooja Rekha Sunita Anjali Neha Shreya Swati Radha Geeta Fatima Aisha Nisha Deepa Revathi Padma Savitri Rupali Isha Tanvi Mahima Kiran Bhavna Jyoti".split()
M = "Rahul Arjun Vikram Suresh Ramesh Kiran Amit Sanjay Manoj Rohan Karthik Venkat Arun Deepak Imran Faisal Naveen Prakash Harish Gopal Nikhil Mohan Ashok Rajesh Sunil Dev Yash Pranav Vivek Anil".split()
S = "Reddy Sharma Iyer Patel Nair Gupta Khan Das Rao Naidu Shah Mehta Joshi Kulkarni Menon Banerjee Singh Desai Pillai Verma Yadav Kapoor Bhat Thakkar Chowdhury".split()
DX = ["Septic shock", "Community-acquired pneumonia", "Post-op CABG, day 2", "Acute pancreatitis", "Diabetic ketoacidosis",
      "COPD exacerbation", "Stroke, post-thrombolysis", "Acute MI, post-PCI", "Diabetic foot sepsis", "Dengue with shock",
      "Traumatic brain injury", "Post-op bowel resection"]
IV = ["500 ml fluid bolus complete", "ABG drawn, result pending", "Antibiotic dose given", "Oxygen raised to 6 L/min",
      "Head of bed raised to 30°", "Sedation reviewed", "Shift assessment recorded", "Central line site checked"]
NAME = {"hr": "HR", "map": "MAP", "spo2": "SpO₂", "rr": "RR"}

def names(pool, n):
    seen = set()
    while len(seen) < n:
        seen.add(random.choice(pool) + " " + random.choice(S))
    return list(seen)

def ser(base, delta=0, ramp=0, back=0, dip=None, noise=1.0):
    out = []
    for i in range(72):  # 72 hourly points, last one is "now"
        v = base + random.uniform(-noise, noise)
        k = i - (72 - ramp)
        if ramp and k >= 0:
            v += delta * k / (ramp - 1)
            if back and i >= 72 - back:
                v -= delta * 0.6 * (i - (72 - back) + 1) / back
        if dip is not None and i == dip:
            v += delta
        out.append(round(v, 1))
    return out

# state -> (band, risk, alert minutes, acked, mods {vital: (delta, ramp, back, dip)}, triggers)
CFG = {
    "red_two":  ("red", 84, 4, 0, {"spo2": (-13, 5), "rr": (11, 5), "hr": (30, 5)}, ["spo2", "rr"]),
    "red_tie":  ("red", 78, 9, 0, {"hr": (45, 4), "spo2": (-6, 4)}, ["hr"]),
    "red_new":  ("red", 78, 0, 0, {"spo2": (-12, 3), "hr": (25, 3)}, ["spo2"]),
    "red_ack":  ("red", 71, 14, 1, {"map": (-22, 8), "hr": (28, 8)}, ["map"]),
    "amber_slow": ("amber", None, 0, 0, {"spo2": (-6, 24), "rr": (5, 24)}, ["spo2"]),
    "amber_near": ("amber", None, 0, 0, {"spo2": (-5, 12), "rr": (6, 12), "hr": (15, 12)}, ["spo2"]),
    "amber_rec":  ("amber", None, 0, 0, {"spo2": (-8, 12, 4), "hr": (20, 12, 4)}, ["spo2"]),
    "nosignal": ("nosig", None, 0, 0, {}, []),
    "falsealarm": ("stable", None, 0, 0, {"spo2": (-18, 0, 0, 68)}, []),
    "dip": ("stable", None, 0, 0, {"hr": (30, 0, 0, 55)}, []),
    "stable": ("stable", None, 0, 0, {}, []),
}
states = (["red_two", "red_tie", "red_new", "red_ack"] + ["amber_slow"] * 4 + ["amber_near"] * 2 + ["amber_rec"] * 2
          + ["nosignal"] * 2 + ["falsealarm"] * 2 + ["dip"] * 2 + ["stable"] * 82)
random.shuffle(states)
sexes = ["F"] * 50 + ["M"] * 50
random.shuffle(sexes)
fn, mn = names(F, 50), names(M, 50)
nurses = names(F + M, 30)

pts = []
for i, (stt, sex) in enumerate(zip(states, sexes)):
    band, risk, mins, acked, mods, trig = CFG[stt]
    h = HOSP[i // 25][0]
    base = dict(hr=random.randint(62, 92), spo2=random.randint(95, 99), rr=random.randint(12, 18))
    sysb, diab = random.randint(110, 132), random.randint(66, 82)
    base["map"] = round((sysb + 2 * diab) / 3)
    series = {v: ser(base[v], *mods.get(v, (0, 0)), noise={"hr": 2, "map": 2, "spo2": 0.5, "rr": 0.8}[v]) if len(mods.get(v, ())) < 3
              else ser(base[v], mods[v][0], mods[v][1], mods[v][2], noise=1) for v in base}
    if "falsealarm" == stt or stt == "dip":
        v = "spo2" if stt == "falsealarm" else "hr"
        series[v] = ser(base[v], mods[v][0], 0, 0, mods[v][3], noise=0.5)
    cur = {v: round(series[v][-1]) for v in series}
    if stt == "amber_near": risk = random.randint(55, 58)
    elif band == "amber": risk = random.randint(36, 50) if stt == "amber_slow" else random.randint(36, 42)
    elif band == "stable": risk = random.randint(5, 28)
    elif band == "nosig": risk = None
    sd = round(cur["map"] * 3 / 2 - cur["map"] * 0.0)  # placeholder, replaced below
    sbp = round(cur["map"] + (sysb - base["map"]) * 1.0)
    dbp = round((3 * cur["map"] - sbp) / 2)
    arrow = lambda v: "↓" if mods.get(v, (0,))[0] < 0 else "↑"
    pts.append(dict(
        id=f"{h}-B{i % 25 + 1:02d}", hosp=h, name=(fn if sex == "F" else mn).pop(),
        age=random.randint(24, 84), sex=sex, dx=random.choice(DX), state=stt, band=band, risk=risk,
        trig=[f"{NAME[v]} {cur[v]} {arrow(v)}" for v in trig], alertMin=mins, acked=acked,
        improving=stt == "amber_rec", suppressed=stt == "falsealarm",
        lastSeen=random.choice([40, 95]) if stt == "nosignal" else 0,
        cur=cur, sbp=sbp, dbp=dbp, temp=round(random.uniform(36.6, 37.3) + (1.1 if band == "red" else 0), 1),
        nurse=random.choice(nurses), ext=random.randint(4100, 4999),
        iv=random.sample(IV, 3), series=series))
# one no-signal bed was amber before, so it must never show green
ns = [p for p in pts if p["state"] == "nosignal"]
ns[0]["was"] = "amber"; ns[1]["was"] = "green"
pts.sort(key=lambda p: p["id"])
data = dict(hospitals=[dict(id=a, name=b, city=c) for a, b, c in HOSP], patients=pts, suppressedBase=14)
open("../data.js", "w").write("// Generated by tools/gen_data.py. Don't edit by hand.\nwindow.DEMO = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n")
print(len(pts), sum(p["sex"] == "F" for p in pts), {b: sum(p["band"] == b for p in pts) for b in ("red", "amber", "nosig", "stable")})

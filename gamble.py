#!/usr/bin/env python3
"""
Edge Simulator — Kelly Criterion + Monte Carlo
Single file, stdlib only. python3 gamble.py
ponytail: no persistence/charts export. Add when persistence needed: json save + matplotlib.
"""
import math, random, sys

# ── ANSI ──
R="\033[0m"; D="\033[2m"; B="\033[1m"; G="\033[92m"; C="\033[96m"; Y="\033[93m"; RE="\033[91m"; M="\033[95m"; W="\033[97m"
BG="\033[42m\033[30m"; GR="\033[90m"

def clr(s,c): return f"{c}{s}{R}"
def hr(ch="─",w=62): return GR+ch*w+R
def box(title, w=62):
    print(f"\n{GR}┌{'─'*w}┐{R}")
    print(f"{GR}│{R} {B}{title:<{w-1}}{R}{GR}│{R}")
    print(f"{GR}└{'─'*w}┘{R}")

def inp(prompt, default=None, cast=float):
    d = f" {D}[{default}]{R}" if default is not None else ""
    while True:
        try:
            raw = input(f"  {C}›{R} {prompt}{d}: {W}").strip()
            print(R, end="")
            if not raw and default is not None: return default
            if not raw: print(f"    {RE}required{R}"); continue
            return cast(raw)
        except ValueError: print(f"    {RE}invalid number{R}")
        except (EOFError, KeyboardInterrupt): print(); raise SystemExit

def inp_opt(prompt, default=None):
    try: return input(f"  {C}›{R} {prompt}{D} [{default}]{R}: {W}").strip() or default
    except (EOFError, KeyboardInterrupt): print(); raise SystemExit
    finally: print(R, end="")

# ── Math ──
def kelly(b, p):
    """b = net odds (decimal-1), p = win prob. f* = (bp - q)/b"""
    q = 1-p
    if b <= 0: return 0
    return (b*p - q) / b

def kelly_stats(p, dec_odds):
    b = dec_odds - 1
    f = kelly(b, p)
    q = 1-p
    ev = p*b - q  # EV per unit staked
    # expected log growth per bet at f
    if f>0:
        g = p*math.log(1+f*b) + q*math.log(1-f) if f<1 else float('-inf')
        # doubling time approx
        dbl = math.log(2)/g if g>0 else float('inf')
    else:
        g = 0; dbl=float('inf')
    edge = p - 1/dec_odds  # prob edge vs implied
    implied = 1/dec_odds
    return dict(b=b,f=f,ev=ev,g=g,dbl=dbl,edge=edge,implied=implied)

def odds_to_decimal(s):
    """parse odds string: 2.5 / +150 / -110 / 5/2"""
    s=s.strip()
    if "/" in s and s.replace("/","").replace(".","").replace("-","").isdigit():
        # fractional
        a,b = s.split("/")
        try: return float(a)/float(b)+1
        except: pass
    if s.startswith("+") or (s.startswith("-") and s[1:].replace(".","").isdigit()):
        try:
            v=float(s)
            return v/100+1 if v>0 else 100/abs(v)+1
        except: pass
    return float(s)

def monte_carlo(bankroll, p, dec_odds, f, n_bets, n_sims, seed=None):
    if seed is not None: random.seed(seed)
    b = dec_odds - 1
    finals=[]
    bust=0
    paths=[]  # sample 50 paths for sparkline
    for i in range(n_sims):
        br=bankroll
        hist=[br]
        for _ in range(n_bets):
            if br<=0.01: break
            stake = br * f
            # cap stake at bankroll
            stake = min(stake, br)
            if random.random() < p:
                br += stake*b
            else:
                br -= stake
            hist.append(br)
        finals.append(br)
        if br < bankroll*0.1: bust+=1  # 90% drawdown = bust-ish
        if len(paths)<50: paths.append(hist)
    finals.sort()
    mean=sum(finals)/len(finals)
    median=finals[len(finals)//2]
    p5=finals[int(len(finals)*0.05)]
    p95=finals[int(len(finals)*0.95)]
    p10=finals[int(len(finals)*0.10)]
    p90=finals[int(len(finals)*0.90)]
    hi=max(finals); lo=min(finals)
    profit_rate=sum(1 for x in finals if x>bankroll)/len(finals)
    ruined=sum(1 for x in finals if x<1)/len(finals)
    return dict(finals=finals, mean=mean, median=median, p5=p5, p95=p95, p10=p10, p90=p90,
                hi=hi, lo=lo, bust=bust/n_sims, profit_rate=profit_rate, ruined=ruined, paths=paths)

def sparkline(vals, w=48, h=7):
    if not vals: return ""
    # resample to w
    if len(vals)>w:
        step=len(vals)/w
        vals=[vals[int(i*step)] for i in range(w)]
    else:
        vals=list(vals)
    lo=min(vals); hi=max(vals)
    rng=hi-lo if hi!=lo else 1
    # h rows
    rows=[]
    for r in range(h):
        thresh=hi - r*(rng/h)
        nxt=hi - (r+1)*(rng/h)
        line=""
        for v in vals:
            if v>=thresh: line+="█"
            elif v>=nxt: line+="▄"
            else: line+=" "
        rows.append(line)
    return "\n".join(f"    {GR}│{R}{row}{GR}│{R}" for row in rows)

def hist_ascii(finals, bankroll, w=52, bins=18):
    lo=min(finals); hi=max(finals)
    if hi==lo: return f"    {D}all outcomes = {hi:,.0f}{R}"
    # log-ish bins if wide range
    # linear bins
    bw=(hi-lo)/bins
    counts=[0]*bins
    for v in finals:
        idx=min(int((v-lo)/bw), bins-1)
        counts[idx]+=1
    mx=max(counts)
    lines=[]
    for i,c in enumerate(counts):
        l=lo+i*bw; r=l+bw
        bar="█"*max(1, int(c/mx*(w-14))) if c else ""
        flag=""
        if bankroll>=l and bankroll<r: flag=f" {Y}◀ buy-in{R}"
        # mark bust region
        lines.append(f"    {GR}{l:>7,.0f}┤{R} {G}{bar:<{w-14}}{R} {D}{c:>4}{R}{flag}")
    lines.append(f"    {GR}{'─'*(w-6)} start {bankroll:,.0f}{R}")
    return "\n".join(lines)

def parlay_combined(legs):
    """legs = [(p, dec), ...] → (p_comb, dec_comb). Assumes independence."""
    pc=1; dc=1
    for p,d in legs: pc*=p; dc*=d
    return pc, dc

def fmt_money(x): return f"${x:,.2f}" if x<1e6 else f"${x/1e3:,.1f}k" if x<1e9 else f"${x/1e6:.2f}M"

# ── Screens ──
def screen_kelly():
    box("KELLY CRITERION  —  optimal bet sizing", 62)
    print(f"  {D}Formula: f* = (bp − q) / b   b=net odds  p=win prob  q=1−p{R}")
    print(f"  {D}Enter prob as 0.55 or 55% • odds as decimal (2.5), American (+150/-110), or fractional (5/2){R}\n")
    p_raw = inp_opt("Win probability (e.g. 55% or 0.55)", "55%")
    p_raw=p_raw.strip()
    if p_raw.endswith("%"): p=float(p_raw[:-1])/100
    else:
        v=float(p_raw)
        p=v/100 if v>1 else v
    if not 0<p<1: print(f"  {RE}p must be 0-1{R}"); return
    o_raw = inp_opt("Decimal / American / fractional odds", "2.00")
    try: dec=odds_to_decimal(o_raw)
    except: print(f"  {RE}bad odds{R}"); return
    b=dec-1
    s=kelly_stats(p, dec)
    f=s['f']
    print(f"\n{hr()}")
    print(f"  {W}{B}Implied prob:{R} {s['implied']*100:.2f}%   {D}vs your {p*100:.2f}%  edge {s['edge']*100:+.2f}pp{R}")
    ev_s=f"{s['ev']:+.4f}"
    print(f"  {W}{B}EV per $1 staked:{R} {clr(ev_s, G if s['ev']>0 else RE)}   {D}(overround-free){R}")
    print(f"  {W}{B}Net odds b:{R} {b:.3f}  {D}(decimal {dec:.3f}){R}")
    print(f"{hr()}")
    if f<=0:
        print(f"\n  {RE}{B}✘  f* = {f*100:.2f}%  —  DON'T BET{R}")
        print(f"  {D}No edge. Kelly says 0. Negative EV at these odds.{R}")
        return
    # cap display at 100%
    fcap=min(f,1.0)
    print(f"\n  {BG}  KELLY  {R}  {B}{W}f* = {f*100:.2f}% of bankroll{R}  {D}(full Kelly){R}")
    if f>0.25: print(f"       {Y}⚠ large — variance will be brutal. Use fractional.{R}")
    # fractional table
    print(f"\n  {GR}┌─────────┬──────────┬──────────────┬──────────────┐{R}")
    print(f"  {GR}│{R} {D}Fraction{R} {GR}│{R} {D}Bet %   {R} {GR}│{R} {D}Growth/bet{R} {GR}│{R} {D}Volatility{R}  {GR}│{R}")
    print(f"  {GR}├─────────┼──────────┼──────────────┼──────────────┤{R}")
    for frac,label in [(1,"Full"),(0.5,"Half"),(0.25,"Quarter"),(0.33,"Third")]:
        ff=fcap*frac
        gg = p*math.log(1+ff*b)+ (1-p)*math.log(1-ff) if ff<1 else float('-inf')
        # variance proxy
        vol = ff*math.sqrt(p*(1-p))*b  # rough
        mark=" ●" if frac==0.5 else "  "
        print(f"  {GR}│{R}{mark}{label:<7}{GR}│{R} {ff*100:6.2f}% {GR}│{R} {gg:+9.4%}  {GR}│{R} {vol:>10.3f} {GR}│{R}")
    print(f"  {GR}└─────────┴──────────┴──────────────┴──────────────┘{R}")
    br = inp("Bankroll", 1000.0)
    stake = br*fcap
    print(f"\n  {D}On {fmt_money(br)} bankroll:{R}")
    print(f"    Full Kelly stake:  {B}{fmt_money(stake)}{R}  {D}({f*100:.2f}%){R}")
    print(f"    Half Kelly stake:  {G}{fmt_money(br*fcap*0.5)}{R}  {D}({f*50:.2f}%)  ← recommended{R}")
    print(f"    Quarter Kelly:     {fmt_money(br*fcap*0.25)}")
    if s['g']>0:
        print(f"\n  {D}At full Kelly: ~{s['dbl']:.1f} bets to double (median). Half Kelly ~{s['dbl']*2:.1f}.{R}")
        print(f"  {D}Long-run growth maximised, but drawdowns ~50% likely. Half Kelly = 75% growth, ~½ variance.{R}")

def screen_monte():
    box("MONTE CARLO  —  bankroll simulation", 62)
    br = inp("Starting bankroll", 1000.0)
    p_raw = inp_opt("Win probability", "55%")
    p_raw=p_raw.strip()
    if p_raw.endswith("%"): p=float(p_raw[:-1])/100
    else:
        v=float(p_raw); p=v/100 if v>1 else v
    o_raw = inp_opt("Decimal / American / fractional odds", "2.00")
    try: dec=odds_to_decimal(o_raw)
    except: print(f"  {RE}bad odds{R}"); return
    # suggest kelly
    s=kelly_stats(p, dec)
    print(f"  {D}Kelly f* = {s['f']*100:.2f}%  (Half {s['f']*50:.2f}%){R}")
    f_raw = inp_opt("Bet size as % of bankroll (e.g. 5% or 0.05)", f"{max(0,s['f']*50):.2f}%" if s['f']>0 else "2%")
    f_raw=f_raw.strip()
    if f_raw.endswith("%"): f=float(f_raw[:-1])/100
    else:
        v=float(f_raw); f=v/100 if v>1 and v<=100 else v
    n_bets = inp("Number of bets (horizon)", 500, cast=int)
    n_sims = inp("Simulations", 5000, cast=int)
    n_sims = max(100, min(n_sims, 50000))
    print(f"\n  {D}Running {n_sims:,} sims × {n_bets} bets…{R}")
    r=monte_carlo(br, p, dec, f, n_bets, n_sims)
    print(f"{hr()}")
    # summary tiles
    print(f"  {B}Final bankroll after {n_bets} bets  ({f*100:.2f}% sizing, {p*100:.1f}% win, {dec:.2f}x){R}\n")
    def tile(label,val, color=W):
        return f"{GR}┌──────────────┐{R}\n{GR}│{R} {D}{label:<12}{R} {GR}│{R}\n{GR}│{R} {color}{val:>12}{R} {GR}│{R}\n{GR}└──────────────┘{R}"
    # crude tile row via text
    print(f"  {D}Mean{R}  {W}{fmt_money(r['mean']):>10}{R}   {D}Median{R} {G}{fmt_money(r['median']):>10}{R}   {D}Best{R}  {fmt_money(r['hi']):>10}   {D}Worst{R} {RE}{fmt_money(r['lo']):>10}{R}")
    print(f"  {D}P5{R}    {fmt_money(r['p5']):>10}   {D}P10{R}   {fmt_money(r['p10']):>10}   {D}P90{R}  {fmt_money(r['p90']):>10}   {D}P95{R}   {fmt_money(r['p95']):>10}")
    print(f"\n  Profit (>start): {G}{r['profit_rate']*100:.1f}%{R}   Ruined (<$1): {RE}{r['ruined']*100:.1f}%{R}   90% drawdown: {Y}{r['bust']*100:.1f}%{R}")
    roi_med=(r['median']/br-1)*100
    roi_mean=(r['mean']/br-1)*100
    print(f"  Median ROI: {roi_med:+.1f}%   Mean ROI: {roi_mean:+.1f}%   {D}(mean > median = right-skew){R}")
    print(f"\n  {B}Distribution (final bankroll){R}")
    print(hist_ascii(r['finals'], br))
    # sample paths
    print(f"\n  {B}Sample paths (50 sims, resampled){R}  {D}— equity curves{R}")
    # median path approximation: pick path closest to median final
    # just show 3 representative sparklines: p10 median p90 path-ish by final sorting? use synthetic
    # use actual stored paths - pick low/med/high
    paths=sorted(r['paths'], key=lambda h: h[-1])
    if paths:
        for label,path in [("Worst",paths[0]), ("Median",paths[len(paths)//2]), ("Best",paths[-1])]:
            print(f"\n  {D}{label} → {fmt_money(path[-1]):>10}{R}")
            print(sparkline(path))
    print(f"\n  {D}Tip: if P5 is near 0, size down. Half Kelly usually puts P5 > 40% of start.{R}")

def screen_lab():
    box("LAB  —  Kelly → Monte Carlo sweep", 62)
    p_raw = inp_opt("Win probability", "55%")
    p_raw=p_raw.strip()
    if p_raw.endswith("%"): p=float(p_raw[:-1])/100
    else:
        v=float(p_raw); p=v/100 if v>1 else v
    o_raw = inp_opt("Odds", "2.00")
    try: dec=odds_to_decimal(o_raw)
    except: print(f"  {RE}bad odds{R}"); return
    br = inp("Bankroll", 1000.0)
    n_bets = inp("Bets per sim", 300, cast=int)
    n_sims = inp("Sims per fraction", 2000, cast=int)
    s=kelly_stats(p, dec)
    fstar=max(0,s['f'])
    if fstar==0: print(f"  {RE}No edge — sweep meaningless. f*=0{R}"); return
    fracs=[0.25,0.5,0.75,1.0,1.5]
    print(f"\n  {D}Sweeping {len(fracs)} fractions of Kelly (f*={fstar*100:.2f}%) over {n_sims:,} sims each…{R}\n")
    print(f"  {GR}{'Frac':>6} {'Bet%':>7} {'Median':>10} {'Mean':>10} {'P5':>10} {'Ruin%':>7} {'Profit%':>8}{R}")
    print(f"  {GR}{'─'*64}{R}")
    best=None
    for frac in fracs:
        f=fstar*frac
        if f>=1: f=0.99
        r=monte_carlo(br,p,dec,f,n_bets,n_sims)
        tag = f" {G}◀ half{R}" if frac==0.5 else f" {Y}◀ full{R}" if frac==1.0 else ""
        ruin = r['ruined']*100
        col = RE if ruin>10 else Y if ruin>2 else G
        print(f"  {frac:5.2f}× {f*100:6.2f}% {fmt_money(r['median']):>10} {fmt_money(r['mean']):>10} {fmt_money(r['p5']):>10} {clr(f'{ruin:5.1f}%',col)} {r['profit_rate']*100:7.1f}%{tag}")
        if best is None or r['median']>best[1]: best=(frac,r['median'])
    print(f"\n  {D}Best median at {best[0]:.2f}× Kelly. Full Kelly maximises log-growth but spikes ruin.{R}")
    print(f"  {G}→ Half Kelly is the usual sweet spot: ~75% of max growth, ~½ the swings.{R}")

def screen_risk():
    box("RISK OF RUIN  —  streaks & drawdown", 62)
    p_raw = inp_opt("Win probability", "55%")
    p_raw=p_raw.strip()
    if p_raw.endswith("%"): p=float(p_raw[:-1])/100
    else:
        v=float(p_raw); p=v/100 if v>1 else v
    q=1-p
    print(f"\n  {D}Streak probabilities (independent bets){R}")
    print(f"  {GR}┌──────┬──────────┬─────────────────────┐{R}")
    print(f"  {GR}│{R} {D}Streak{R} {GR}│{R} {D}Prob    {R} {GR}│{R} {D}1-in               {R} {GR}│{R}")
    print(f"  {GR}├──────┼──────────┼─────────────────────┤{R}")
    for n in [5,8,10,12,15,20]:
        pl=q**n; pw=p**n
        print(f"  {GR}│{R} {n:>2} L  {GR}│{R} {pl:7.2%}  {GR}│{R} 1 in {1/pl:>7,.0f}       {GR}│{R}")
        print(f"  {GR}│{R} {n:>2} W  {GR}│{R} {pw:7.2%}  {GR}│{R} 1 in {1/pw:>7,.0f}       {GR}│{R}")
    print(f"  {GR}└──────┴──────────┴─────────────────────┘{R}")
    # drawdown at fixed fraction
    f = inp("Bet fraction for drawdown calc (e.g. 0.05)", 0.05)
    if f>=1: f=0.5
    b_raw=inp_opt("Net odds b (decimal-1) if known, else Enter for even", "1.0")
    try: b=float(b_raw)
    except: b=1
    # expected consecutive losses to 50% drawdown: (1-f)^n = 0.5
    if f<1:
        n50=math.log(0.5)/math.log(1-f) if f!=0 else float('inf')
        n90=math.log(0.1)/math.log(1-f) if f!=0 else float('inf')
        print(f"\n  {D}At {f*100:.1f}% per bet:{R}")
        print(f"    {n50:.1f} consecutive losses → −50% bankroll")
        print(f"    {n90:.1f} consecutive losses → −90% bankroll")
        prob50=q**math.ceil(n50) if n50!=float('inf') else 0
        print(f"    P(≥{math.ceil(n50)} losses in a row ever in 500 bets) ≈ {1-(1-prob50)**500:.1%}  {D}(approx){R}")
    # gambler's ruin approx for even odds
    print(f"\n  {D}Gambler's ruin (even money, fixed stake) — quick approx:{R}")
    target = inp("Target bankroll (e.g. 2000)", 2000.0)
    start = inp("Start bankroll", 1000.0)
    stake = inp("Stake per bet", 10.0)
    units_start=start/stake; units_target=target/stake
    if p!=0.5:
        r=q/p
        # prob hit target before 0 from i units
        prob = (1 - r**units_start)/(1 - r**units_target) if r!=1 else units_start/units_target
        print(f"    P(hit {fmt_money(target)} before $0): {G}{prob*100:.1f}%{R}  {D}at {p*100:.1f}% win rate{R}")
    else:
        print(f"    P(hit target): {units_start/units_target*100:.1f}%  {D}(50% win = fair game){R}")

def screen_parlay():
    box("PARLAY — combined legs (independent)", 62)
    print(f"  {D}Enter legs: prob + odds. Empty prob to finish. Legs assumed independent.{R}")
    print(f"  {D}Example: 60% @ 1.91, 55% @ 2.10, 70% @ 1.50{R}")
    legs=[]
    n=1
    while True:
        raw = inp_opt(f"Leg {n} prob (empty=done)", "")
        if not raw: break
        raw=raw.strip()
        try:
            p=float(raw[:-1])/100 if raw.endswith("%") else (float(raw)/100 if float(raw)>1 else float(raw))
        except: print(f"  {RE}bad prob{R}"); continue
        if not 0<p<1: print(f"  {RE}p 0-1{R}"); continue
        o_raw = inp_opt(f"Leg {n} odds", "1.91")
        try: dec=odds_to_decimal(o_raw)
        except: print(f"  {RE}bad odds{R}"); continue
        legs.append((p,dec))
        print(f"    {G}leg {n}: p={p*100:.1f}% dec={dec:.3f}{R}")
        n+=1
        if n>12:
            print(f"  {Y}12 legs max{R}"); break
    if len(legs)<2: print(f"  {RE}need ≥2 legs{R}"); return
    pc, dc = parlay_combined(legs)
    print(f"\n{hr()}")
    print(f"  {W}{B}Combined: p={pc*100:.3f}%  dec={dc:.3f}  b={dc-1:.3f}  implied={1/dc*100:.3f}%{R}")
    s=kelly_stats(pc, dc)
    f=s['f']
    print(f"  EV per $1: {G if s['ev']>0 else RE}{s['ev']:+.5f}{R}   {'DON’T BET' if f<=0 else ''}  edge {s['edge']*100:+.2f}pp")
    # per-leg vs combined
    print(f"\n  {D}Leg breakdown:{R}")
    for i,(p,d) in enumerate(legs,1):
        si=kelly_stats(p,d)
        print(f"    {i}. p={p*100:5.2f}% dec={d:5.3f} f*={si['f']*100:6.2f}% ev={si['ev']:+.4f}")
    if f<=0:
        print(f"\n  {RE}{B}✘ Parlay f*={f*100:.2f}% — negative EV. Bet singles if any leg has edge, else don’t bet.{R}")
        print(f"  {D}Note: parlay Kelly is always ≤ best single when legs independent — it concentrates variance.{R}")
        return
    fcap=min(f,1)
    print(f"\n  {BG}  PARLAY KELLY  {R}  {B}f*={f*100:.2f}%  half={(fcap*50):.2f}%  quarter={(fcap*25):.2f}%{R}")
    # compare vs best single
    best = max(kelly_stats(p,d)['f'] for p,d in legs)
    print(f"  {D}Best single f*={best*100:.2f}% vs parlay {f*100:.2f}%  —  {('parlay bigger (rare)' if f>best else 'singles safer (usual)')}{R}")
    br = inp("Bankroll", 1000.0)
    print(f"  Parlay half-Kelly stake: {G}{fmt_money(br*fcap*0.5)}{R}")
    # quick monte option
    go = inp_opt("Run Monte Carlo on parlay? (y/N)", "n")
    if go.lower().startswith("y"):
        f_use = br * fcap * 0.5 / br  # half kelly fraction
        nb = inp("Bets (parlays placed)", 300, cast=int)
        ns = inp("Sims", 3000, cast=int)
        ns=max(100,min(ns,20000))
        r=monte_carlo(br, pc, dc, f_use, nb, ns)
        print(f"  Mean {fmt_money(r['mean'])}  Median {fmt_money(r['median'])}  P5 {fmt_money(r['p5'])}  P95 {fmt_money(r['p95'])}  Ruin {(r['ruined']*100):.1f}%")

BANNER = f"""{G}
  ██████╗  █████╗ ███╗   ███╗██████╗ ██╗     ███████╗
  ██╔════╝ ██╔══██╗████╗ ████║██╔══██╗██║     ██╔════╝
  ██║  ███╗███████║██╔████╔██║██████╔╝██║     █████╗
  ██║   ██║██╔══██║██║╚██╔╝██║██╔══██╗██║     ██╔══╝
  ╚██████╔╝██║  ██║██║ ╚═╝ ██║██████╔╝███████╗███████╗
   ╚═════╝ ╚═╝  ╚═╝╚═╝     ╚═╝╚═════╝ ╚══════╝╚══════╝{R}
  {GR}  ┌─────────────────────────────────────────────┐{R}
  {GR}  │{R}  {C}EDGE SIMULATOR{R}  {D}Kelly · Monte Carlo · Risk · Parlay{R}  {GR}│{R}
  {GR}  └─────────────────────────────────────────────┘{R}
  {D}  stdlib only  •  no deps  •  type a number, get an edge{R}
"""

MENU = f"""
  {W}{B}Pick:{R}
   {G}1{R}  Kelly Criterion         {D}— optimal bet size{R}
   {C}2{R}  Monte Carlo             {D}— simulate N bets × M sims{R}
   {M}3{R}  Lab (sweep)             {D}— Kelly fractions head-to-head{R}
   {Y}4{R}  Risk / Streaks          {D}— ruin & drawdown math{R}
   {C}5{R}  Parlay                  {D}— combined legs (independent){R}
   {D}q{R}  Quit
"""

def main():
    print(BANNER)
    # quick demo numbers if non-interactive: allow args
    if len(sys.argv)>1:
        # gamble.py kelly 0.55 2.0  /  gamble.py sim 1000 0.55 2.0 0.05 500 5000
        cmd=sys.argv[1].lower()
        if cmd in ("kelly","k"):
            p=float(sys.argv[2].strip("%"))/100 if "%" in sys.argv[2] else float(sys.argv[2])
            if p>1: p/=100
            dec=odds_to_decimal(sys.argv[3])
            s=kelly_stats(p,dec)
            print(f"p={p} dec={dec} f*={s['f']*100:.2f}% ev={s['ev']:+.4f} g={s['g']:.4f}")
            return
        if cmd in ("sim","monte","mc"):
            br=float(sys.argv[2]); p=float(sys.argv[3]); dec=odds_to_decimal(sys.argv[4]); f=float(sys.argv[5]); nb=int(sys.argv[6]); ns=int(sys.argv[7]) if len(sys.argv)>7 else 5000
            if p>1: p/=100
            if f>1: f/=100
            r=monte_carlo(br,p,dec,f,nb,ns,seed=42)
            print(f"mean {r['mean']:.0f} median {r['median']:.0f} p5 {r['p5']:.0f} p95 {r['p95']:.0f} ruin {r['ruined']*100:.1f}%")
            return
        if cmd in ("parlay","acc","acca","multi"):
            # usage: gamble.py parlay 0.60@1.91 0.55@2.10 0.70@1.50  [bankroll]
            legs=[]
            for tok in sys.argv[2:]:
                if "@" in tok:
                    ps, os_ = tok.split("@",1)
                    p=float(ps.strip("%"))/100 if "%" in ps else float(ps)
                    if p>1: p/=100
                    dec=odds_to_decimal(os_)
                    legs.append((p,dec))
                else:
                    # bare bankroll
                    try: float(tok); continue
                    except: pass
            if len(legs)<2: print("need ≥2 legs like 0.60@1.91 0.55@2.10"); return
            pc,dc=parlay_combined(legs)
            s=kelly_stats(pc,dc)
            print(f"legs {len(legs)} p={pc*100:.3f}% dec={dc:.3f} f*={s['f']*100:.2f}% ev={s['ev']:+.4f}")
            for i,(p,d) in enumerate(legs,1):
                si=kelly_stats(p,d); print(f"  {i}. p={p*100:.2f}% dec={d:.3f} f*={si['f']*100:.2f}%")
            return
    while True:
        print(MENU)
        try: choice=input(f"  {C}›{R} {W}choice{R} {D}[1]{R}: ").strip().lower() or "1"
        except (EOFError, KeyboardInterrupt): print(f"\n  {D}bye{R}"); break
        if choice in ("q","quit","exit"): print(f"  {D}bye — bet small, edge big{R}"); break
        try:
            if choice=="1": screen_kelly()
            elif choice=="2": screen_monte()
            elif choice=="3": screen_lab()
            elif choice=="4": screen_risk()
            elif choice=="5": screen_parlay()
            else: print(f"  {RE}unknown: {choice}{R}")
        except SystemExit: print(f"  {D}bye{R}"); break
        except Exception as e: print(f"  {RE}error: {e}{R}")

if __name__=="__main__":
    main()

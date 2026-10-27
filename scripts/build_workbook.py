"""Regenerates data/Fox_Creek_Scratch_SG.xlsx (requires openpyxl). Formulas are written without cached values; open in Excel/LibreOffice to recalculate."""
import numpy as np
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.comments import Comment
from openpyxl.worksheet.datavalidation import DataValidation

F = "Arial"
def font(**k): return Font(name=F, **k)
BLUE = "0000FF"; GREEN = "008000"
YEL = PatternFill("solid", fgColor="FFFF00")
HDR = PatternFill("solid", fgColor="1F3864")
GREY = PatternFill("solid", fgColor="7F7F7F")
thin = Side(style="thin", color="BFBFBF")
box = Border(left=thin, right=thin, top=thin, bottom=thin)

def hdr(ws, row, col, text, fill=HDR):
    c = ws.cell(row=row, column=col, value=text)
    c.font = font(bold=True, color="FFFFFF"); c.fill = fill
    c.alignment = Alignment(wrap_text=True, vertical="center")
    return c

def inp(ws, row, col, val):
    c = ws.cell(row=row, column=col, value=val)
    c.font = font(color=BLUE); c.fill = YEL; c.border = box
    return c

holes = [(1,4,356,1),(2,3,150,9),(3,4,262,15),(4,3,156,7),(5,3,158,13),(6,5,397,17),(7,3,150,11),
         (8,3,168,3),(9,4,301,5),(10,3,143,12),(11,4,333,6),(12,3,97,18),(13,3,154,14),(14,4,260,4),
         (15,3,129,8),(16,4,321,2),(17,3,149,10),(18,3,118,16)]

wb = Workbook()

# ============================================================ How To
ws = wb.active; ws.title = "How To"
lines = [
 ("Fox Creek Scratch Strokes Gained (data-anchored)", True),
 ("Green tees, 3,802 yards, par 62. Baseline = a scratch golfer, built from published scratch statistics (Shot Scope, Arccos) rather than tour tables plus guesses. Hole expectations are calibrated so the 18 holes sum to the Course Rating + 2.4, i.e. an average scratch round (the rating itself is a good day).", False),
 ("", False),
 ("How to use", True),
 ("1. Log every shot on 'Shot Log': Round ID, Hole, Start lie, Start distance, End lie, End distance, Penalty.", False),
 ("2. Lies: T = tee, F = fairway/fringe, R = rough, S = sand, X = recovery (blocked, punch-out), G = green, H = holed.", False),
 ("3. Distances: yards for T/F/R/S/X, FEET for G. Leave End distance blank when End lie is H. Tee shots on par 4/5 use the hole's tee-model value whatever you enter for distance; par-3 tee shots use the distance you enter.", False),
 ("4. Penalty: 1 if the shot cost a penalty stroke. For OB, log the re-tee as the next shot from T with Penalty 1.", False),
 ("5. Each shot's next row starts where the previous one ended. Add the Round ID on 'Rounds' for category totals. Delete the EXAMPLE rows once you have logged a real round.", False),
 ("", False),
 ("How the baseline is built (see 'Scratch Data')", True),
 ("Putting: E(putts) = 2 - P(one-putt) + P(three-putt) + P(four-putt), from Shot Scope / Arccos scratch make and three-putt rates by distance.", False),
 ("Approach (50-250 yds): E = 1 + GIR x E(putts from on-green proximity) + (1 - GIR) x E(after a miss), using scratch GIR, proximity and short-game data. Rough and sand use factors on the fairway inputs.", False),
 ("Around the green (<= 50 yds): from scratch up-and-down rates (<25 yds 63%, 25-50 yds 32%, sand save 37%). From 150-250 yds the table takes the better of going for the green and laying up; beyond 250 it is 1 + a layup/advance to a fairway-rough blend.", False),
 ("Tee shots on par 4/5: the tee model on 'Course' (best club for a scratch golfer given fairway width, OB/trees and club dispersion). Par 3s: the approach table from the tee.", False),
 ("Course calibration: the gap between the raw 18-hole total and the target (Course Rating + 2.4, an average scratch round) is spread across holes and applied ONLY to shots that start off the green, so putting is always measured straight against the scratch putting data.", False),
 ("", False),
 ("Reading the numbers", True),
 ("SG per shot = E(start) - E(end) - 1 - penalty. Positive = better than an average scratch golfer at Fox Creek. Over a full 18, total SG = (Course Rating + 2.4) - your score.", False),
 ("Categories: OTT = tee shots on par 4/5; APP = shots from >30 yds (incl. par-3 tee shots); ARG = <=30 yds off the green; PUTT = on the green.", False),
 ("Yellow cells with blue text are inputs. Every published number and every assumption is labelled on 'Inputs' and 'Scratch Data'. 'Tour Ref' shows the scratch baseline next to tour values as a sanity check.", False),
]
for i, (t, b) in enumerate(lines, start=1):
    c = ws.cell(row=i, column=1, value=t); c.font = font(bold=b, size=14 if i == 1 else 11)
    c.alignment = Alignment(wrap_text=True, vertical="top")
ws.column_dimensions["A"].width = 125

# ============================================================ Inputs
wi = wb.create_sheet("Inputs")
wi["A1"] = "Assumptions and parameters"; wi["A1"].font = font(bold=True, size=13)
params = [
 ("COURSE", None, None, None),
 ("Course rating (Green tees, men)", 59.9, "CR", "PUBLISHED: Golfify / 18Birdies listings for Fox Creek Golf Club, Smyrna GA (Green 3,802 yds, 59.9 / 105). Confirm in the GHIN course lookup."),
 ("Good-day gap added to the CR target", 2.4, "GOOD", "DERIVED. A Course Rating is a scratch golfer's good day: a Handicap Index uses the best 8 of 20 differentials, and the mean of the best 8 of 20 normal draws sits 0.93 sigma below the mean. With a scratch round-to-round sigma of ~2.6 strokes, CR + 2.4 is an AVERAGE scratch round, which is what the Shot Scope / Arccos tables describe. Set 0 to calibrate to the CR itself."),
 ("Stroke-index weight (0 = spread evenly, 1 = fully by SI)", 0, "LAMBDA", "How the course adjustment is spread across holes. ASSUMPTION."),
 ("Off-green anchor E for spreading the hole adjustment", 1.85, "G0", "A shot's share of the hole adjustment = (E - G0)/(E_tee - G0), 0 on the green. 1.85 ~ scratch putts per GIR (Shot Scope). ASSUMPTION."),
 ("Teed-ball bonus on par-3 tee shots (strokes)", 0, "TEEB", "Positive = a teed ball is easier than the same yardage from the fairway. Tour data actually runs the other way (par-3 tee shots ~0.1 HARDER than same-length fairway shots, because of guarded greens), so 0 is used and the course calibration absorbs Fox Creek specifics. ASSUMPTION."),
 ("APPROACH MODEL", None, None, None),
 ("Effective putt-distance factor (Jensen correction)", 0.70, "JEN", "Proximity varies shot to shot and E(putts) is concave, so E over the spread < E at the mean. Using 0.7 x mean proximity reproduces tour fairway values from tour GIR/proximity to ~0.05. ASSUMPTION."),
 ("Rough: GIR factor", 0.80, "RGF", "GIR from rough = fairway GIR x this. Shot Scope: fairway-vs-rough GIR advantage 'up to 25%'. ASSUMPTION within that."),
 ("Rough: proximity factor", 1.25, "RPF", "On-green proximity from rough = fairway x this. golfity estimate: rough adds 30-40% to proximity. ASSUMPTION."),
 ("Rough: extra strokes after a miss", 0.10, "RMA", "ASSUMPTION."),
 ("Fairway bunker (>50 yds): GIR factor", 0.65, "SGF", "ASSUMPTION."),
 ("Fairway bunker: proximity factor", 1.30, "SPF", "ASSUMPTION."),
 ("Fairway bunker: extra strokes after a miss", 0.20, "SMA", "ASSUMPTION."),
 ("Rough around the green: extra strokes vs fairway lie", 0.20, "RARG", "Chip/pitch from rough vs fairway/fringe. ASSUMPTION."),
 ("Fairway share after a layup/advance shot", 0.70, "FWSL", "For shots from >250 yds. ASSUMPTION."),
 ("Layup/advance distance from fairway (yds)", 220, "LAYF", "Scratch 3-wood/hybrid from the fairway on a long second shot; a deliberate layup never leaves less than 30 yds. ASSUMPTION."),
 ("Advance distance from rough (yds)", 190, "LAYR", "ASSUMPTION."),
 ("Advance distance from a fairway bunker (yds)", 170, "LAYS", "ASSUMPTION."),
 ("Recovery: yards gained by a punch-out", 100, "XADV", "Recovery (X) = 1 + penalty + blend of fairway/rough at (distance - this). ASSUMPTION."),
 ("Recovery: extra strokes", 0.10, "XPEN", "ASSUMPTION."),
 ("TEE MODEL", None, None, None),
 ("Fairway share of in-play tee shots", 0.70, "FWS", "In-play tee shots blended 70% fairway / 30% rough. ASSUMPTION."),
 ("Default fairway width (yds, tree line to tree line)", 45, "WID", "From you: ~45 yds with trees both sides on basically every hole; hole 1 OB both sides; holes 3 and 16 OB right."),
 ("Scratch club 1 (driver) distance", 262, "D1", "Shot Scope P-avg for scratch is 285 (solid strikes). Plain averages run ~8-10% lower (3H avg 197 vs P-avg 219; Arccos 0-4.9 band 244 all ages). 262 = 285 x 0.92."),
 ("Scratch club 1 (driver) sigma %", 0.075, "S1", "DERIVED: Arccos (Stagner) 7% of 0-5 index drives finish >40 yds from fairway centre -> sigma ~22 yds; tour 65-70 yd cone -> ~16-18 yds. Scratch ~20 yds = 7.5% of 262."),
 ("Scratch club 2 (3-wood) distance", 245, "D2", "Shot Scope P-avg 261-267 x 0.92."),
 ("Scratch club 2 (3-wood) sigma %", 0.08, "S2", "DERIVED: Shot Scope scratch 3-wood hits only ~1% more fairways than driver despite ~18 yds less, implying similar absolute spread (~20 yds) = ~8% of 245."),
 ("Scratch club 3 (3-hybrid) distance", 203, "D3", "Shot Scope scratch 3H: P-avg 219, plain average 197."),
 ("Scratch club 3 (3-hybrid) sigma %", 0.075, "S3", "ASSUMPTION (no published figure): ~15 yds."),
 ("Scratch club 4 (5-iron) distance", 185, "D4", "Shot Scope P-avg 200 x 0.92."),
 ("Scratch club 4 (5-iron) sigma %", 0.07, "S4", "ASSUMPTION (no published figure): ~13 yds."),
 ("Your club 1 (driver) distance", 290, "M1", "Your tee clubs for the 'Your best club' columns. Replace sigma % with sim-measured numbers (offline std dev / distance)."),
 ("Your club 1 (driver) sigma %", 0.10, "MS1", "PLACEHOLDER."),
 ("Your club 2 (7-wood) distance", 215, "M2", ""),
 ("Your club 2 (7-wood) sigma %", 0.085, "MS2", "PLACEHOLDER."),
 ("Your club 3 (2-iron) distance", 240, "M3", ""),
 ("Your club 3 (2-iron) sigma %", 0.09, "MS3", "PLACEHOLDER."),
 ("Your club 4 (5-iron) distance", 186, "M4", ""),
 ("Your club 4 (5-iron) sigma %", 0.075, "MS4", "PLACEHOLDER."),
]
hdr(wi, 3, 1, "Parameter"); hdr(wi, 3, 2, "Value"); hdr(wi, 3, 3, "Notes / source")
ref = {}
r = 4
for lab, val, key, note in params:
    if val is None:
        c = wi.cell(row=r, column=1, value=lab); c.font = font(bold=True); c.fill = PatternFill("solid", fgColor="D9E1F2")
    else:
        wi.cell(row=r, column=1, value=lab).font = font()
        inp(wi, r, 2, val)
        wi.cell(row=r, column=3, value=note).font = font(size=9)
        ref[key] = f"Inputs!$B${r}"
    r += 1
wi.column_dimensions["A"].width = 52; wi.column_dimensions["B"].width = 10; wi.column_dimensions["C"].width = 120
wi.freeze_panes = "A4"

# ============================================================ Scratch Data
sd = wb.create_sheet("Scratch Data")
sd["A1"] = "Scratch-golfer anchor data (blue = editable). Interpolated on 'Baseline'."; sd["A1"].font = font(bold=True, size=13)
# Putting block A:E
for j, h in enumerate(["Feet", "P(1-putt)", "P(3-putt)", "P(4-putt)", "E(putts)"], start=1): hdr(sd, 4, j, h)
putt = [(1,1.00,0,0),(2,0.99,0,0),(3,0.94,0,0),(4,0.84,0.001,0),(5,0.73,0.002,0),(6,0.62,0.003,0),
        (8,0.47,0.006,0),(10,0.36,0.012,0),(12,0.29,0.02,0),(15,0.22,0.03,0),(20,0.14,0.055,0.001),
        (25,0.095,0.09,0.002),(30,0.065,0.13,0.003),(40,0.035,0.20,0.005),(50,0.025,0.27,0.01),
        (60,0.018,0.34,0.015),(80,0.010,0.45,0.025),(100,0.005,0.53,0.035)]
for i, (f, p1, p3, p4) in enumerate(putt, start=5):
    sd.cell(row=i, column=1, value=f).font = font()
    inp(sd, i, 2, p1); inp(sd, i, 3, p3); inp(sd, i, 4, p4)
    sd.cell(row=i, column=5, value=f"=2-B{i}+C{i}+D{i}").font = font(); sd.cell(row=i, column=5).number_format = "0.000"
PX = "'Scratch Data'!$A$5:$A$22"; PE = "'Scratch Data'!$E$5:$E$22"
# Approach block G:J
for j, h in enumerate(["Yards (fairway)", "GIR", "On-green proximity (ft)", "E after a miss"], start=7): hdr(sd, 4, j, h)
appr = [(50,0.80,14,2.45),(75,0.75,17,2.48),(100,0.68,21,2.50),(125,0.62,25,2.55),(150,0.55,30,2.60),
        (175,0.47,36,2.65),(200,0.38,42,2.72),(225,0.30,48,2.80),(250,0.22,55,2.90)]
for i, (y, g, p, m) in enumerate(appr, start=5):
    sd.cell(row=i, column=7, value=y).font = font()
    inp(sd, i, 8, g); inp(sd, i, 9, p); inp(sd, i, 10, m)
AX = "'Scratch Data'!$G$5:$G$13"; AG = "'Scratch Data'!$H$5:$H$13"; AP = "'Scratch Data'!$I$5:$I$13"; AM = "'Scratch Data'!$J$5:$J$13"
# ARG fairway block L:M
hdr(sd, 4, 12, "Yards (fairway/fringe lie)"); hdr(sd, 4, 13, "E (strokes to hole out)")
arg = [(5,2.18),(10,2.30),(15,2.38),(20,2.44),(25,2.50),(30,2.58),(40,2.68),(50,2.80)]
for i, (y, e) in enumerate(arg, start=5):
    sd.cell(row=i, column=12, value=y).font = font(); inp(sd, i, 13, e)
CX = "'Scratch Data'!$L$5:$L$12"; CE = "'Scratch Data'!$M$5:$M$12"
# Sand greenside block O:P
hdr(sd, 4, 15, "Yards (greenside bunker)"); hdr(sd, 4, 16, "E (strokes to hole out)")
sand = [(5,2.55),(10,2.62),(15,2.68),(20,2.75),(30,2.86),(40,3.00),(50,3.08)]
for i, (y, e) in enumerate(sand, start=5):
    sd.cell(row=i, column=15, value=y).font = font(); inp(sd, i, 16, e)
SX = "'Scratch Data'!$O$5:$O$11"; SE = "'Scratch Data'!$P$5:$P$11"

notes = [
 ("PUTTING - published scratch data used", True),
 ("Shot Scope 0-hcp make %, fine bands (MyGolfSpy): 0-3 ft 98%, 3-6 ft 76%, 6-9 ft 49%, 9-12 ft 34%, 12-18 ft 19%, 18-24 ft 12%, 24-30 ft 7%, 30+ ft 4%.", False),
 ("Shot Scope 0-hcp make %, broad bands (Shot Scope blog): 0-6 ft 92.8%, 6-12 ft 42.8%, 12-18 ft 25.1%, 18-24 ft 14.5%, 24-30 ft 8.3%, 30+ ft 4.3%. The two tables disagree at 12-18 ft (19% vs 25%); anchors use the midpoint.", False),
 ("Three-putts: Arccos 1-5 index: 9.4% from 20-25 ft, 19.6% from 25+ ft; Arccos/Stagner scratch ~25% from 36-40 ft. Shot Scope scratch: 3% of holes (0.8/round), 4.6 ft left on average after a first putt from 30 ft (implies ~12-15% from 30 ft). Anchors sit between the two sources. Tour reference (PGA Tour/Broadie): 20 ft 2%, 30 ft 5%, 40 ft 10%, 60 ft 23%.", False),
 ("Check: Shot Scope scratch = 29.9 putts/round, 1.85 putts per GIR. E(putts) here at 18 ft = 1.88, at 15 ft = 1.81.", False),
 ("APPROACH - published scratch data used", True),
 ("Shot Scope scratch proximity INCLUDING misses (Golf Monthly): 50-100 yds 26 ft, 100-150 yds 38 ft, 150-200 yds 54 ft, 200+ yds 92 ft; 17% of approaches inside 15 ft, 42% inside 30 ft. Scratch GIR overall 52-59% (two Shot Scope figures). Tour GIR by distance used for the shape of the curve.", False),
 ("GIR, on-green proximity and miss distance were chosen so that GIR x on-green + (1-GIR) x miss reproduces those band averages: implied miss distances 53 / 59 / 70 / 111 ft, and overall GIR ~55% for a typical mix of approach lengths. The on-green proximity and GIR split is DERIVED, not published.", False),
 ("E after a miss = short-game value for the typical miss (chip/pitch, some sand), rising with approach length.", False),
 ("AROUND THE GREEN - published scratch data used", True),
 ("Shot Scope scratch (MyGolfSpy short-game chart): up-and-down <25 yds 63%, 25-50 yds 32%, inside 50 yds overall 54%, sand save 37%, average proximity after the shot 11 ft, shots to finish from inside 50 yds 2.45. E ~ 3 - up-and-down% + ~0.03 (double chips and three-putts minus holed shots).", False),
 ("TOUR comparison on 'Tour Ref': scratch sits ~+0.05 to +0.15 behind tour on putts, ~+0.1 around the green, and ~+0.2 to +0.3 on approaches, in line with Broadie's finding that approach play is the largest scratch-to-tour gap.", False),
 ("SOURCES", True),
 ("https://mygolfspy.com/news-opinion/putting-make-percentage-by-handicap-full-chart-are-you-above-or-below-average/", False),
 ("https://shotscope.com/blog/practice-green/stats-and-data/putting-make-percentages-by-handicap-how-do-you-compare/", False),
 ("https://mygolfspy.com/news-opinion/shot-scope-case-study/  (three-putt stats by handicap)", False),
 ("https://golf.com/instruction/putting/how-likely-to-three-putt-play-smart/  (Arccos / Lou Stagner three-putt by distance)", False),
 ("https://eu.arccosgolf.com/blogs/community/pros-vs-joes-analyzing-3-putts", False),
 ("https://www.golfmonthly.com/features/scratch-vs-10-vs-20-handicap-how-the-stats-compare  (Shot Scope: GIR, proximity, up-and-down, putting)", False),
 ("https://www.golfmonthly.com/features/how-close-to-the-pin-do-amateur-golfers-hit-their-approach-shots  (Shot Scope proximity by distance band)", False),
 ("https://www.golfmonthly.com/features/how-many-greens-in-regulation-does-an-average-golfer-hit  (Shot Scope GIR by handicap, tour 66.75%)", False),
 ("https://mygolfspy.com/news-opinion/instruction/how-good-is-your-short-game-performance-chart-by-handicap/  (Shot Scope short game by handicap)", False),
 ("https://golfingfocus.com/what-percentage-of-putts-do-pros-make-tv-does-not-tell-the-story/  (PGA Tour make and three-putt by distance)", False),
]
rr = 26
for t, b in notes:
    c = sd.cell(row=rr, column=1, value=t); c.font = font(bold=b, size=10 if not b else 11)
    c.alignment = Alignment(wrap_text=True, vertical="top")
    sd.merge_cells(start_row=rr, start_column=1, end_row=rr, end_column=16)
    sd.row_dimensions[rr].height = 15 if b or len(t) < 120 else 30
    rr += 1
for j in range(1, 17): sd.column_dimensions[sd.cell(row=4, column=j).column_letter].width = 13
sd.column_dimensions["F"].width = 3; sd.column_dimensions["K"].width = 3; sd.column_dimensions["N"].width = 3

# ============================================================ Baseline (scratch, interpolated)
bs = wb.create_sheet("Baseline")
bs["A1"] = "Scratch expected strokes to hole out, built from 'Scratch Data' and 'Inputs'. Yards for F/R/S/X, feet for G."; bs["A1"].font = font(bold=True)
for j, h in enumerate(["Yards", "F", "R", "S", "X"], start=1): hdr(bs, 2, j, h)
hdr(bs, 2, 8, "Feet"); hdr(bs, 2, 9, "G")
YDS = list(range(5, 605, 5)); FT = list(range(1, 101))
Y0, Y1 = 3, 3 + len(YDS) - 1
F0, F1 = 3, 3 + len(FT) - 1
YR = f"Baseline!$A${Y0}:$A${Y1}"
FCOL = f"Baseline!$B${Y0}:$B${Y1}"; RCOL = f"Baseline!$C${Y0}:$C${Y1}"; SCOL = f"Baseline!$D${Y0}:$D${Y1}"; XCOL = f"Baseline!$E${Y0}:$E${Y1}"
TBL = f"Baseline!$B${Y0}:$E${Y1}"; LH = "Baseline!$B$2:$E$2"
GCOL = f"Baseline!$I${F0}:$I${F1}"

def interp(X, Y, d):
    k = f"MATCH({d},{X},1)"
    return (f"(INDEX({Y},{k})+({d}-INDEX({X},{k}))*(INDEX({Y},MIN({k}+1,ROWS({X})))-INDEX({Y},{k}))"
            f"/MAX(INDEX({X},MIN({k}+1,ROWS({X})))-INDEX({X},{k}),0.0001))")
def yd5(expr): return f"MIN(MAX(ROUND(({expr})/5,0)*5,5),600)"
def LF(expr): return f"INDEX({FCOL},MATCH({yd5(expr)},{YR},0))"
def LR(expr): return f"INDEX({RCOL},MATCH({yd5(expr)},{YR},0))"
def LX(expr): return f"INDEX({XCOL},MATCH({yd5(expr)},{YR},0))"
def EP(expr): return f"INDEX({GCOL},MIN(MAX(ROUND({expr},0),1),100))"

JEN=ref['JEN']; LAYF=ref['LAYF']; LAYR=ref['LAYR']; LAYS=ref['LAYS']; RPF=ref['RPF']; SPF=ref['SPF']; XADV=ref['XADV']
for i, y in enumerate(YDS):
    r = Y0 + i
    bs.cell(row=r, column=1, value=y).font = font()
    d = f"$A{r}"
    gF = interp(AX, AG, d); pr = interp(AX, AP, d); ms = interp(AX, AM, d)
    layF = f"(1+{ref['FWSL']}*{LF(f'MAX({d}-{LAYF},30)')}+(1-{ref['FWSL']})*{LR(f'MAX({d}-{LAYF},30)')})"
    layR = f"(1+{ref['FWSL']}*{LF(f'MAX({d}-{LAYR},30)')}+(1-{ref['FWSL']})*{LR(f'MAX({d}-{LAYR},30)')}+{ref['RMA']})"
    layS = f"(1+{ref['FWSL']}*{LF(f'MAX({d}-{LAYS},30)')}+(1-{ref['FWSL']})*{LR(f'MAX({d}-{LAYS},30)')}+{ref['SMA']})"
    appF = f"(1+{gF}*{EP(f'{JEN}*{pr}')}+(1-{gF})*{ms})"
    appR = f"(1+{gF}*{ref['RGF']}*{EP(f'{JEN}*{pr}*{RPF}')}+(1-{gF}*{ref['RGF']})*({ms}+{ref['RMA']}))"
    appS = f"(1+{gF}*{ref['SGF']}*{EP(f'{JEN}*{pr}*{SPF}')}+(1-{gF}*{ref['SGF']})*({ms}+{ref['SMA']}))"
    fF = f"=IF({d}<=50,{interp(CX, CE, d)},IF({d}<=250,MIN({appF},{layF}),{layF}))"
    fR = f"=IF({d}<=50,$B{r}+{ref['RARG']},IF({d}<=250,MIN({appR},{layR}),{layR}))"
    fS = f"=IF({d}<=50,{interp(SX, SE, d)},IF({d}<=250,MIN({appS},{layS}),{layS}))"
    fX = f"=1+{ref['XPEN']}+0.6*{LF(f'MAX({d}-{XADV},15)')}+0.4*{LR(f'MAX({d}-{XADV},15)')}"
    for j, fm in zip((2, 3, 4, 5), (fF, fR, fS, fX)):
        c = bs.cell(row=r, column=j, value=fm); c.font = font(); c.number_format = "0.000"
for i, f in enumerate(FT):
    r = F0 + i
    bs.cell(row=r, column=8, value=f).font = font()
    c = bs.cell(row=r, column=9, value=f"={interp(PX, PE, f'$H{r}')}"); c.font = font(); c.number_format = "0.000"
for col, w in zip("ABCDEFGHI", [8, 9, 9, 9, 9, 3, 3, 8, 9]): bs.column_dimensions[col].width = w
bs.freeze_panes = "A3"

# ============================================================ Course (tee model + calibration)
wc = wb.create_sheet("Course")
ch = ["Hole", "Par", "Yards", "SI", "Width (yds)", "Trouble", "From-tee approach E (par 3 / generic)",
      "Scratch E: driver", "Scratch E: 3-wood", "Scratch E: 3-hybrid", "Scratch E: 5-iron", "Tee model E", "Scratch best club",
      "Raw scratch E", "SI weight", "Course adj (a_h)", "Adjusted scratch E",
      "Your E: driver", "Your E: 7-wood", "Your E: 2-iron", "Your E: 5-iron", "Your best club"]
for j, h in enumerate(ch, start=1): hdr(wc, 1, j, h)
wc.row_dimensions[1].height = 45

def tee_model(i, dist, sig):
    w = f"$E{i}"; L = f"MAX($C{i}-{dist},15)"
    pin = f"(2*NORMSDIST({w}/2/({sig}*{dist}))-1)"
    ein = f"({ref['FWS']}*{LF(L)}+(1-{ref['FWS']})*{LR(L)})"
    ex = LX(L)
    pob = f'IF($F{i}="OB",1-{pin},IF(OR($F{i}="OBR",$F{i}="OBL"),(1-{pin})/2,0))'
    return f"(1+{pin}*{ein}+(1-{pin}-{pob})*{ex}+{pob})/(1-{pob})"

for i, (h, p, y, si) in enumerate(holes, start=2):
    for j, v in enumerate((h, p, y, si), start=1):
        c = wc.cell(row=i, column=j, value=v); c.font = font(color=BLUE if j > 1 else "000000")
    if p > 3:
        c = wc.cell(row=i, column=5, value=f"={ref['WID']}"); c.font = font(color=GREEN)
        inp(wc, i, 6, {1: "OB", 3: "OBR", 16: "OBR"}.get(h, "X"))
    wc.cell(row=i, column=7, value=f"={LF(f'$C{i}')}-{ref['TEEB']}").font = font()
    for k, (dk, sk) in enumerate(zip(["D1", "D2", "D3", "D4"], ["S1", "S2", "S3", "S4"])):
        wc.cell(row=i, column=8 + k, value=f'=IF($B{i}=3,"",{tee_model(i, ref[dk], ref[sk])})').font = font()
    wc.cell(row=i, column=12, value=f'=IF($B{i}=3,"",MIN(H{i}:K{i}))').font = font()
    wc.cell(row=i, column=13, value=f'=IF($B{i}=3,"",INDEX({{"driver","3-wood","3-hybrid","5-iron"}},MATCH(L{i},H{i}:K{i},0)))').font = font()
    wc.cell(row=i, column=14, value=f'=IF($B{i}=3,G{i},L{i})').font = font()
    wc.cell(row=i, column=15, value=f"=(1-{ref['LAMBDA']})/18+{ref['LAMBDA']}*(19-D{i})/171").font = font()
    wc.cell(row=i, column=16, value=f"=($B$23-$N$20)*O{i}").font = font()
    wc.cell(row=i, column=17, value=f"=N{i}+P{i}").font = font()
    for k, (dk, sk) in enumerate(zip(["M1", "M2", "M3", "M4"], ["MS1", "MS2", "MS3", "MS4"])):
        wc.cell(row=i, column=18 + k, value=f'=IF($B{i}=3,"",{tee_model(i, ref[dk], ref[sk])})').font = font()
    wc.cell(row=i, column=22, value=f'=IF($B{i}=3,"",INDEX({{"driver","7-wood","2-iron","5-iron"}},MATCH(MIN(R{i}:U{i}),R{i}:U{i},0)))').font = font()
    for col in list(range(7, 13)) + list(range(14, 22)):
        wc.cell(row=i, column=col).number_format = "0.00"
wc["A20"] = "Total"; wc["A20"].font = font(bold=True)
for col in "BCGLNOPQ":
    wc[f"{col}20"] = f"=SUM({col}2:{col}19)"; wc[f"{col}20"].font = font(bold=True); wc[f"{col}20"].number_format = "0.00"
wc["A22"] = "Check"; wc["A22"].font = font(bold=True)
wc["A23"] = "Calibration target (CR + good-day gap)"; wc["B23"] = f"={ref['CR']}+{ref['GOOD']}"; wc["B23"].font = font(color=GREEN)
wc["A24"] = "Adjusted total minus target (should be 0)"; wc["B24"] = "=ROUND(Q20-B23,4)"
wc["A25"] = "Total course adjustment (raw scratch total vs target)"; wc["B25"] = "=P20"
for rr_ in (23, 24, 25): wc[f"A{rr_}"].font = font()
wc["A27"] = ("Tee model (par 4/5): E = 1 + P(in play) x E(leave; fairway/rough blend) + P(trees) x E(recovery) [+ OB handled as stroke and distance, closed form]. "
             "P(in play) = 2*Phi(width/2 / sigma) - 1, sigma = club sigma% x club distance; misses split evenly left/right. Scratch E for the hole = best of four clubs. "
             "Par 3s: the scratch approach table from the tee minus the teed-ball bonus. The course adjustment is spread across holes (SI weight) and, within a hole, across off-green shots only.")
wc["A27"].font = font(size=9); wc["A27"].alignment = Alignment(wrap_text=True, vertical="top"); wc.merge_cells("A27:V29")
wc["A30"] = "Holes, pars, yardages, stroke index: Golfify scorecard for Fox Creek Golf Club (Green tees). Width/trouble from you."; wc["A30"].font = font(size=9)
for j in range(1, 23): wc.column_dimensions[wc.cell(row=1, column=j).column_letter].width = 10
wc.freeze_panes = "E2"
C_PAR = "Course!$B$2:$B$19"; C_H = "Course!$A$2:$A$19"; C_RAW = "Course!$N$2:$N$19"; C_ADJ = "Course!$P$2:$P$19"; C_FIN = "Course!$Q$2:$Q$19"

# ============================================================ Shot Log
wl = wb.create_sheet("Shot Log")
lh = ["Round ID", "Hole", "Start lie", "Start dist", "End lie", "End dist", "Penalty", "Note",
      "Category", "E start", "E end", "SG vs scratch", "Par", "Raw E start", "Raw E end", "Hole raw tee E", "Hole adj", "w start", "w end"]
for j, h in enumerate(lh, start=1): hdr(wl, 1, j, h, HDR if j <= 12 else GREY)
wl.row_dimensions[1].height = 30
NROWS = 1500
example = [("EXAMPLE",1,"T",356,"F",102,0,"driver"),("EXAMPLE",1,"F",102,"G",22,0,"full SW"),
           ("EXAMPLE",1,"G",22,"G",3,0,""),("EXAMPLE",1,"G",3,"H",None,0,""),
           ("EXAMPLE",2,"T",150,"G",25,0,"8i"),("EXAMPLE",2,"G",25,"H",None,0,"")]
def rawE(lie, d, par, hole):
    return (f'IF({lie}="H",0,IF({lie}="G",{EP(d)},IF({lie}="T",IF({par}=3,{LF(d)}-{ref["TEEB"]},INDEX({C_RAW},MATCH({hole},{C_H},0))),'
            f'INDEX({TBL},MATCH({yd5(d)},{YR},0),MATCH({lie},{LH},0)))))')
def wgt(lie, e, tee):
    return f'IF(OR({lie}="G",{lie}="H"),0,IF({lie}="T",1,MIN(1,MAX(0,({e}-{ref["G0"]})/MAX({tee}-{ref["G0"]},0.01)))))'
for r in range(2, NROWS + 2):
    if r - 2 < len(example):
        for j, v in enumerate(example[r - 2], start=1): inp(wl, r, j, v)
    wl.cell(row=r, column=13, value=f'=IF($B{r}="","",INDEX({C_PAR},MATCH($B{r},{C_H},0)))')
    wl.cell(row=r, column=14, value=f'=IF($C{r}="","",{rawE(f"$C{r}", f"$D{r}", f"$M{r}", f"$B{r}")})')
    wl.cell(row=r, column=15, value=f'=IF($C{r}="","",{rawE(f"$E{r}", f"$F{r}", f"$M{r}", f"$B{r}")})')
    wl.cell(row=r, column=16, value=f'=IF($B{r}="","",INDEX({C_RAW},MATCH($B{r},{C_H},0)))')
    wl.cell(row=r, column=17, value=f'=IF($B{r}="","",INDEX({C_ADJ},MATCH($B{r},{C_H},0)))')
    wl.cell(row=r, column=18, value=f'=IF($C{r}="","",{wgt(f"$C{r}", f"$N{r}", f"$P{r}")})')
    wl.cell(row=r, column=19, value=f'=IF($C{r}="","",{wgt(f"$E{r}", f"$O{r}", f"$P{r}")})')
    wl.cell(row=r, column=9, value=f'=IF($C{r}="","",IF($C{r}="G","PUTT",IF(AND($C{r}="T",$M{r}>3),"OTT",IF($D{r}<=30,"ARG","APP"))))')
    wl.cell(row=r, column=10, value=f'=IF($C{r}="","",$N{r}+$Q{r}*$R{r})')
    wl.cell(row=r, column=11, value=f'=IF($C{r}="","",$O{r}+$Q{r}*$S{r})')
    wl.cell(row=r, column=12, value=f'=IF($C{r}="","",$J{r}-$K{r}-1-N($G{r}))')
    for j in range(9, 20): wl.cell(row=r, column=j).font = font()
    for j in (10, 11, 12, 14, 15, 16, 17, 18, 19): wl.cell(row=r, column=j).number_format = "0.00"
dv = DataValidation(type="list", formula1='"T,F,R,S,X,G"', allow_blank=True); wl.add_data_validation(dv); dv.add(f"C2:C{NROWS+1}")
dv2 = DataValidation(type="list", formula1='"F,R,S,X,G,H"', allow_blank=True); wl.add_data_validation(dv2); dv2.add(f"E2:E{NROWS+1}")
wl.freeze_panes = "A2"
for j, w in enumerate([12, 6, 8, 9, 8, 9, 8, 16, 9, 8, 8, 12, 6, 9, 9, 10, 9, 8, 8], start=1):
    wl.column_dimensions[wl.cell(row=1, column=j).column_letter].width = w
wl["H1"].comment = Comment("Optional: 'cut corner', 'aimed away (OB)', 'flyer', 'plugged'. Useful for comparing strategies and explaining outliers.", "Claude")

# ============================================================ Rounds
wr = wb.create_sheet("Rounds")
rh = ["Round ID", "Holes logged", "Score", "OTT", "APP", "ARG", "PUTT", "Total SG", "Target - score (18-hole check)"]
for j, h in enumerate(rh, start=1): hdr(wr, 1, j, h)
wr.row_dimensions[1].height = 30
L = "'Shot Log'!"
for r in range(2, 52):
    if r == 2: inp(wr, 2, 1, "EXAMPLE")
    else: wr.cell(row=r, column=1).fill = YEL
    A = f"$A{r}"
    wr.cell(row=r, column=2, value=f'=IF({A}="","",SUMPRODUCT(({L}$A$2:$A${NROWS+1}={A})*({L}$E$2:$E${NROWS+1}="H")))')
    wr.cell(row=r, column=3, value=f'=IF({A}="","",COUNTIFS({L}$A$2:$A${NROWS+1},{A},{L}$C$2:$C${NROWS+1},"<>")+SUMIFS({L}$G$2:$G${NROWS+1},{L}$A$2:$A${NROWS+1},{A}))')
    for j, cat in zip(range(4, 8), ["OTT", "APP", "ARG", "PUTT"]):
        wr.cell(row=r, column=j, value=f'=IF({A}="","",SUMIFS({L}$L$2:$L${NROWS+1},{L}$A$2:$A${NROWS+1},{A},{L}$I$2:$I${NROWS+1},"{cat}"))')
    wr.cell(row=r, column=8, value=f'=IF({A}="","",SUM(D{r}:G{r}))')
    wr.cell(row=r, column=9, value=f'=IF({A}="","",IF(B{r}=18,Course!$B$23-C{r},"n/a"))')
    for j in range(2, 10):
        wr.cell(row=r, column=j).font = font()
        if j >= 4: wr.cell(row=r, column=j).number_format = "+0.00;-0.00;0.00"
for j, w in enumerate([14, 10, 8, 9, 9, 9, 9, 10, 16], start=1):
    wr.column_dimensions[wr.cell(row=1, column=j).column_letter].width = w
wr.freeze_panes = "A2"

# ============================================================ Tour Ref (sanity check)
tr = wb.create_sheet("Tour Ref")
tr["A1"] = "Sanity check: scratch baseline (this workbook) next to approximate PGA Tour values (Broadie, Every Shot Counts). Positive difference = scratch needs more strokes."; tr["A1"].font = font(bold=True)
for j, h in enumerate(["Situation", "Lie", "Distance", "Tour E (approx.)", "Scratch E (this workbook)", "Scratch - Tour"], start=1): hdr(tr, 3, j, h)
rows = [("Putt", "G", 3, 1.04), ("Putt", "G", 6, 1.34), ("Putt", "G", 10, 1.61), ("Putt", "G", 15, 1.78), ("Putt", "G", 20, 1.87),
        ("Putt", "G", 30, 1.98), ("Putt", "G", 40, 2.06), ("Putt", "G", 60, 2.21),
        ("Chip/pitch", "F", 10, 2.18), ("Chip/pitch", "F", 20, 2.40), ("Chip/pitch", "F", 30, 2.52), ("Pitch", "F", 50, 2.66),
        ("Chip/pitch", "R", 20, 2.59), ("Bunker", "S", 20, 2.53),
        ("Approach", "F", 100, 2.80), ("Approach", "F", 150, 2.95), ("Approach", "F", 200, 3.19), ("Approach", "F", 250, 3.52), ("Long", "F", 300, 3.78),
        ("Approach", "R", 100, 3.02), ("Approach", "R", 150, 3.19), ("Approach", "R", 200, 3.42),
        ("Recovery", "X", 150, 3.80)]
for i, (sit, lie, d, tour) in enumerate(rows, start=4):
    tr.cell(row=i, column=1, value=sit).font = font(); tr.cell(row=i, column=2, value=lie).font = font()
    tr.cell(row=i, column=3, value=d).font = font(); inp(tr, i, 4, tour)
    if lie == "G":
        f = f"={EP(f'$C{i}')}"
    else:
        f = f"=INDEX({TBL},MATCH({yd5(f'$C{i}')},{YR},0),MATCH($B{i},{LH},0))"
    tr.cell(row=i, column=5, value=f).font = font(); tr.cell(row=i, column=5).number_format = "0.00"
    tr.cell(row=i, column=6, value=f"=E{i}-D{i}").font = font(); tr.cell(row=i, column=6).number_format = "+0.00;-0.00;0.00"
tr["A29"] = "Expected pattern (Broadie): scratch loses most to tour on approach play, then driving, then short game and putting. Tour values are approximate and are NOT used in any calculation."
tr["A29"].font = font(size=9)
for j, w in enumerate([12, 6, 9, 14, 20, 14], start=1): tr.column_dimensions[tr.cell(row=3, column=j).column_letter].width = w

wb.save("data/Fox_Creek_Scratch_SG.xlsx")
print("saved")

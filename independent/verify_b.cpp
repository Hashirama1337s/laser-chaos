// verify_b.cpp -- independent checker B for a chain of covering relations of the
// modulated class-B laser stroboscopic map (see SPEC_B.md).
//
// Design choices (made independently of any other verifier):
//  * Time is carried as an explicit third state variable t with dt/dt = 1, so the
//    vector field is autonomous in (t, y, W). Initial sets have t = 0 exactly.
//    After integration the t-component of the enclosure must contain the interval
//    enclosure of T = 2 pi / omega (guards against skipped / wrong-length runs).
//  * Sets are C0Rect2Set (doubleton x + C r0 + B r); initial set is the parallelogram
//    piece itself (C has the chart vectors U, S as columns), so no wrapping at t=0.
//  * Image in the target chart: evaluated twice, (a) on the doubleton structure
//    A(x-Q) + (A C) r0 + (A B) r and (b) on the hull box A(hull - Q); both are
//    rigorous enclosures, their intersection is used.
//  * Chart inverse: exact adjugate formula over interval arithmetic,
//    [U S]^{-1} = [[SW, -Sy], [-UW, Uy]] / (Uy SW - Sy UW), determinant must
//    exclude 0.
//  * Subdivision: uniform initial grid, then adaptive bisection (edges: in s only;
//    full set: in both u and s) up to a depth cap. A check fails as soon as one
//    piece fails at the depth cap or one piece fails with certainty.
//  * All comparisons are explicit bound comparisons: "a < b" is decided as
//    rightBound(a) < leftBound(b).
//  * Disjointness: separating-axis test for convex parallelograms with interval
//    projections onto the four edge normals.
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <string>
#include <vector>
#include <fstream>
#include <sstream>
#include <map>
#include <chrono>
#include <stdexcept>
#include "capd/capdlib.h"

using namespace capd;
using std::string;
using std::vector;

typedef interval I;

struct Chart {
  string name;
  double Q[2], U[2], S[2];
  I A[2][2];  // enclosure of [U S]^{-1}
};
struct HSet { string name; int chart; double c, w, b; };
struct Trans { int src, dst, o; };

static vector<Chart> charts;
static vector<HSet> hsets;
static vector<Trans> transList;

static int findChart(const string& n) {
  for (size_t i = 0; i < charts.size(); ++i) if (charts[i].name == n) return (int)i;
  return -1;
}
static int findSet(const string& n) {
  for (size_t i = 0; i < hsets.size(); ++i) if (hsets[i].name == n) return (int)i;
  return -1;
}
static double parseD(const string& s) {
  char* end = 0;
  double v = strtod(s.c_str(), &end);
  if (end == s.c_str() || *end != '\0') throw std::runtime_error("bad number: " + s);
  return v;
}

static void parseDesign(const char* path) {
  std::ifstream in(path);
  if (!in) throw std::runtime_error(string("cannot open ") + path);
  string line;
  bool gotM = false;
  while (std::getline(in, line)) {
    if (!line.empty() && line.back() == '\r') line.pop_back();
    if (line.empty() || line[0] == '#') continue;
    std::istringstream ss(line);
    vector<string> tok; string t;
    while (ss >> t) tok.push_back(t);
    if (tok.empty()) continue;
    if (tok[0] == "m") {
      if (tok.size() != 2 || tok[1] != "1") throw std::runtime_error("only 'm 1' supported");
      gotM = true;
    } else if (tok[0] == "p") {
      // polynomial line, format compatibility only; ignored (all charts must be affine)
    } else if (tok[0] == "chart") {
      if (tok.size() != 9 || tok[2] != "affine")
        throw std::runtime_error("non-affine or malformed chart rejected: " + line);
      Chart c; c.name = tok[1];
      if (findChart(c.name) >= 0) throw std::runtime_error("duplicate chart " + c.name);
      c.Q[0] = parseD(tok[3]); c.Q[1] = parseD(tok[4]);
      c.U[0] = parseD(tok[5]); c.U[1] = parseD(tok[6]);
      c.S[0] = parseD(tok[7]); c.S[1] = parseD(tok[8]);
      I Uy(c.U[0]), UW(c.U[1]), Sy(c.S[0]), SW(c.S[1]);
      I det = Uy * SW - Sy * UW;
      if (!(det.leftBound() > 0.0 || det.rightBound() < 0.0))
        throw std::runtime_error("singular chart " + c.name);
      c.A[0][0] = SW / det;  c.A[0][1] = -Sy / det;
      c.A[1][0] = -UW / det; c.A[1][1] = Uy / det;
      charts.push_back(c);
    } else if (tok[0] == "set") {
      if (tok.size() != 5) throw std::runtime_error("malformed set: " + line);
      HSet h; h.name = tok[1]; h.chart = findChart(tok[1]);
      if (h.chart < 0) throw std::runtime_error("set without chart: " + h.name);
      if (findSet(h.name) >= 0) throw std::runtime_error("duplicate set " + h.name);
      h.c = parseD(tok[2]); h.w = parseD(tok[3]); h.b = parseD(tok[4]);
      if (!(h.w > 0 && h.b > 0)) throw std::runtime_error("non-positive w/b in " + h.name);
      hsets.push_back(h);
    } else if (tok[0] == "trans") {
      if (tok.size() != 4) throw std::runtime_error("malformed trans: " + line);
      Trans tr; tr.src = findSet(tok[1]); tr.dst = findSet(tok[2]);
      tr.o = (int)parseD(tok[3]);
      if (tr.src < 0 || tr.dst < 0 || (tr.o != 1 && tr.o != -1))
        throw std::runtime_error("bad trans: " + line);
      transList.push_back(tr);
    } else {
      throw std::runtime_error("unknown line: " + line);
    }
  }
  if (!gotM) throw std::runtime_error("missing 'm 1' line");
}

// ---------------------------------------------------------------- dynamics
static I T_period;          // enclosure of 2 pi / omega
static long nIntegrations = 0, nIntegrationFailures = 0;

struct Flow {
  IMap f;
  IOdeSolver solver;
  ITimeMap tm;
  Flow(I a, I eps, I om, I mu, int order)
    : f("par:a,eps,om,mu;var:t,y,W;fun:1,W+a*cos(om*t),mu-(1+eps*W)*(1+exp(y));"),
      solver(f, order), tm(solver) {
    f.setParameter("a", a);
    f.setParameter("eps", eps);
    f.setParameter("om", om);
    f.setParameter("mu", mu);
    // the solver holds its own copy of the vector field: set parameters there too
    solver.getVectorField().setParameter("a", a);
    solver.getVectorField().setParameter("eps", eps);
    solver.getVectorField().setParameter("om", om);
    solver.getVectorField().setParameter("mu", mu);
  }
};

// Image of the parallelogram piece {Q + u U + s S : u in ur, s in sr} of chart cs,
// expressed in chart cd coordinates (u, s). Returns false if integration failed.
static bool imageInChart(Flow& fl, const Chart& cs, I ur, I sr, const Chart& cd, I& uOut, I& sOut) {
  double um = ur.mid().leftBound(), sm = sr.mid().leftBound();
  IVector x0(3), r0(3);
  IMatrix C(3, 3);
  x0[0] = I(0.0);
  x0[1] = I(cs.Q[0]) + I(um) * I(cs.U[0]) + I(sm) * I(cs.S[0]);
  x0[2] = I(cs.Q[1]) + I(um) * I(cs.U[1]) + I(sm) * I(cs.S[1]);
  C[0][0] = 1; C[0][1] = 0; C[0][2] = 0;
  C[1][0] = 0; C[1][1] = cs.U[0]; C[1][2] = cs.S[0];
  C[2][0] = 0; C[2][1] = cs.U[1]; C[2][2] = cs.S[1];
  r0[0] = I(0.0);
  r0[1] = ur - I(um);
  r0[2] = sr - I(sm);
  C0Rect2Set set(x0, C, r0);
  ++nIntegrations;
  IVector hull(3);
  try {
    hull = fl.tm(T_period, set);
  } catch (std::exception& e) {
    ++nIntegrationFailures;
    return false;
  }
  // time guard: the t-component must enclose T
  if (!(hull[0].leftBound() <= T_period.leftBound() && hull[0].rightBound() >= T_period.rightBound())
      || hull[0].rightBound() - hull[0].leftBound() > 1e-8) {
    std::fprintf(stderr, "time guard failed: t = [%.17g, %.17g]\n", hull[0].leftBound(), hull[0].rightBound());
    ++nIntegrationFailures;
    return false;
  }
  IMatrix Ah(3, 3);
  Ah[0][0] = 1; Ah[0][1] = 0; Ah[0][2] = 0;
  Ah[1][0] = 0; Ah[1][1] = cd.A[0][0]; Ah[1][2] = cd.A[0][1];
  Ah[2][0] = 0; Ah[2][1] = cd.A[1][0]; Ah[2][2] = cd.A[1][1];
  IVector Qd(3);
  Qd[0] = I(0.0); Qd[1] = I(cd.Q[0]); Qd[2] = I(cd.Q[1]);
  // (a) doubleton evaluation
  IVector va = Ah * (set.get_x() - Qd) + (Ah * set.get_C()) * set.get_r0() + (Ah * set.get_B()) * set.get_r();
  // (b) hull evaluation
  IVector vb = Ah * (hull - Qd);
  for (int k = 1; k <= 2; ++k) {
    I lo = va[k], hi = vb[k];
    double l = std::max(lo.leftBound(), hi.leftBound());
    double r = std::min(lo.rightBound(), hi.rightBound());
    if (l > r) { // both are enclosures of a nonempty set; empty intersection would be a bug
      std::fprintf(stderr, "empty intersection of enclosures -- instrument error\n");
      ++nIntegrationFailures;
      return false;
    }
    I v(l, r);
    if (k == 1) uOut = v; else sOut = v;
  }
  return true;
}

// ---------------------------------------------------------------- checks
enum Kind { EDGE_MINUS, EDGE_PLUS, STRIP };
struct Piece { I u, s; int depth; };
struct Result { bool ok; long boxes; long refined; double worstMargin; string msg; };

static int MAX_DEPTH = 10;

// decide a piece: returns 1 = pass, 0 = undecided, -1 = certain fail
// margin: how far inside the required region (positive = good)
static int decide(Kind kind, int o, bool leftEdge, I u, I s, const HSet& M, double& margin) {
  I lowM = I(M.c) - I(M.w);   // c - w
  I highM = I(M.c) + I(M.w);  // c + w
  I bM(M.b);
  if (kind == STRIP) {
    double m1 = bM.leftBound() - s.rightBound();   // need s < b
    double m2 = s.leftBound() + bM.leftBound();    // need s > -b
    margin = std::min(m1, m2);
    if (m1 > 0 && m2 > 0) return 1;
    if (s.leftBound() >= bM.rightBound() || s.rightBound() <= -bM.rightBound()) return -1;
    return 0;
  }
  // exit edges: which side is required?
  // E- (left edge): o=+1 -> u < c-w ; o=-1 -> u > c+w
  // E+ (right edge): o=+1 -> u > c+w ; o=-1 -> u < c-w
  bool needBelow = leftEdge ? (o == 1) : (o == -1);
  if (needBelow) {
    margin = lowM.leftBound() - u.rightBound();
    if (margin > 0) return 1;
    if (u.leftBound() >= lowM.rightBound()) return -1;
    return 0;
  } else {
    margin = u.leftBound() - highM.rightBound();
    if (margin > 0) return 1;
    if (u.rightBound() <= highM.leftBound()) return -1;
    return 0;
  }
}

static vector<double> grid(double lo, double hi, int n) {
  vector<double> g(n + 1);
  g[0] = lo; g[n] = hi;
  for (int i = 1; i < n; ++i) {
    double v = lo + (hi - lo) * ((double)i / n);
    if (!(v > g[i - 1]) || !(v < hi)) throw std::runtime_error("grid generation failed");
    g[i] = v;
  }
  return g;
}

static Result runCheck(Flow& fl, Kind kind, const Trans& tr, int nInit) {
  const HSet& N = hsets[tr.src];
  const HSet& M = hsets[tr.dst];
  const Chart& cs = charts[N.chart];
  const Chart& cd = charts[M.chart];
  Result res; res.ok = true; res.boxes = 0; res.refined = 0; res.worstMargin = 1e300;
  vector<Piece> stack;
  I uLeft = I(N.c) - I(N.w), uRight = I(N.c) + I(N.w);
  // s always covers [-b, b] exactly
  vector<double> sg = grid(-N.b, N.b, nInit);
  if (kind == EDGE_MINUS || kind == EDGE_PLUS) {
    I ue = (kind == EDGE_MINUS) ? uLeft : uRight;
    for (int i = 0; i < nInit; ++i) stack.push_back(Piece{ue, I(sg[i], sg[i + 1]), 0});
  } else {
    // u covers [leftBound(c-w), rightBound(c+w)] which contains the exact range
    vector<double> ug = grid(uLeft.leftBound(), uRight.rightBound(), nInit);
    for (int i = 0; i < nInit; ++i)
      for (int j = 0; j < nInit; ++j)
        stack.push_back(Piece{I(ug[i], ug[i + 1]), I(sg[j], sg[j + 1]), 0});
  }
  while (!stack.empty()) {
    Piece p = stack.back(); stack.pop_back();
    ++res.boxes;
    I u, s;
    int verdict;
    double margin = -1e300;
    if (!imageInChart(fl, cs, p.u, p.s, cd, u, s)) verdict = 0;
    else verdict = decide(kind, tr.o, kind == EDGE_MINUS, u, s, M, margin);
    if (verdict == 1) { if (margin < res.worstMargin) res.worstMargin = margin; continue; }
    if (verdict == -1 || p.depth >= MAX_DEPTH) {
      char buf[512];
      std::snprintf(buf, sizeof(buf), "%s piece u=[%.17g,%.17g] s=[%.17g,%.17g] depth %d: image u=[%.10g,%.10g] s=[%.10g,%.10g]",
                    verdict == -1 ? "CERTAIN FAIL" : "UNDECIDED at depth cap",
                    p.u.leftBound(), p.u.rightBound(), p.s.leftBound(), p.s.rightBound(), p.depth,
                    u.leftBound(), u.rightBound(), s.leftBound(), s.rightBound());
      res.ok = false; res.msg = buf;
      return res;
    }
    ++res.refined;
    double sm = p.s.mid().leftBound();
    if (kind == STRIP) {
      double um = p.u.mid().leftBound();
      I ua(p.u.leftBound(), um), ub(um, p.u.rightBound());
      I sa(p.s.leftBound(), sm), sb(sm, p.s.rightBound());
      stack.push_back(Piece{ua, sa, p.depth + 1});
      stack.push_back(Piece{ua, sb, p.depth + 1});
      stack.push_back(Piece{ub, sa, p.depth + 1});
      stack.push_back(Piece{ub, sb, p.depth + 1});
    } else {
      stack.push_back(Piece{p.u, I(p.s.leftBound(), sm), p.depth + 1});
      stack.push_back(Piece{p.u, I(sm, p.s.rightBound()), p.depth + 1});
    }
  }
  return res;
}

// ---------------------------------------------------------------- disjointness
static void vertices(const HSet& h, I vy[4], I vW[4]) {
  const Chart& c = charts[h.chart];
  I us[2] = {I(h.c) - I(h.w), I(h.c) + I(h.w)};
  I ss[2] = {I(-h.b), I(h.b)};
  int k = 0;
  for (int i = 0; i < 2; ++i)
    for (int j = 0; j < 2; ++j) {
      vy[k] = I(c.Q[0]) + us[i] * I(c.U[0]) + ss[j] * I(c.S[0]);
      vW[k] = I(c.Q[1]) + us[i] * I(c.U[1]) + ss[j] * I(c.S[1]);
      ++k;
    }
}
static bool separated(const HSet& a, const HSet& b) {
  I ay[4], aW[4], by[4], bW[4];
  vertices(a, ay, aW); vertices(b, by, bW);
  const Chart* cc[2] = {&charts[a.chart], &charts[b.chart]};
  for (int ci = 0; ci < 2; ++ci) {
    double dirs[2][2] = {{cc[ci]->U[0], cc[ci]->U[1]}, {cc[ci]->S[0], cc[ci]->S[1]}};
    for (int d = 0; d < 2; ++d) {
      I ny(-dirs[d][1]), nW(dirs[d][0]);   // normal to edge direction
      double aMin = 1e300, aMax = -1e300, bMin = 1e300, bMax = -1e300;
      for (int k = 0; k < 4; ++k) {
        I pa = ay[k] * ny + aW[k] * nW;
        I pb = by[k] * ny + bW[k] * nW;
        aMin = std::min(aMin, pa.leftBound()); aMax = std::max(aMax, pa.rightBound());
        bMin = std::min(bMin, pb.leftBound()); bMax = std::max(bMax, pb.rightBound());
      }
      if (aMax < bMin || bMax < aMin) return true;
    }
  }
  return false;
}

// ---------------------------------------------------------------- main
int main(int argc, char** argv) {
  const char* design = "design_chain.txt";
  long mNum = 76, mDen = 1250;
  int order = 12, nEdge = 32, nStrip = 12;
  string probeSrc, probeDst; int probeK = 0;
  for (int i = 1; i < argc; ++i) {
    if (!std::strcmp(argv[i], "--m") && i + 2 < argc) { mNum = atol(argv[i + 1]); mDen = atol(argv[i + 2]); i += 2; }
    else if (!std::strcmp(argv[i], "--order") && i + 1 < argc) order = atoi(argv[++i]);
    else if (!std::strcmp(argv[i], "--nedge") && i + 1 < argc) nEdge = atoi(argv[++i]);
    else if (!std::strcmp(argv[i], "--nstrip") && i + 1 < argc) nStrip = atoi(argv[++i]);
    else if (!std::strcmp(argv[i], "--maxdepth") && i + 1 < argc) MAX_DEPTH = atoi(argv[++i]);
    else if (!std::strcmp(argv[i], "--probe") && i + 3 < argc) { probeSrc = argv[i + 1]; probeDst = argv[i + 2]; probeK = atoi(argv[i + 3]); i += 3; }
    else design = argv[i];
  }
  auto t0 = std::chrono::steady_clock::now();
  std::printf("checker B: design=%s  m=%ld/%ld  order=%d  nEdge=%d  nStrip=%dx%d  maxDepth=%d\n",
              design, mNum, mDen, order, nEdge, nStrip, nStrip, MAX_DEPTH);
  try {
    parseDesign(design);
  } catch (std::exception& e) {
    std::printf("design rejected: %s\nNOT VERIFIED\n", e.what());
    return 1;
  }
  std::printf("parsed %zu charts, %zu h-sets, %zu transitions\n", charts.size(), hsets.size(), transList.size());

  I mu(2.0);
  I eps = I(1.0) / I(25.0);
  I om = I(11.0) / I(10.0);
  I m = I((double)mNum) / I((double)mDen);
  I a = m / eps;
  T_period = I(2.0) * I::pi() / om;
  std::printf("T = [%.17g, %.17g], m/eps = [%.17g, %.17g]\n", T_period.leftBound(), T_period.rightBound(),
              a.leftBound(), a.rightBound());
  std::fflush(stdout);

  Flow fl(a, eps, om, mu, order);
  bool all = true;

  if (probeK > 0) {
    // diagnostic only (not part of the verification): image of single points on the
    // boundary of the source set of each transition into SRC->DST; certifies a violation
    // of (S) if some point image has rightBound(s) < -bM or leftBound(s) > bM.
    for (size_t t = 0; t < transList.size(); ++t) {
      const Trans& tr = transList[t];
      if (hsets[tr.src].name != probeSrc || hsets[tr.dst].name != probeDst) continue;
      const HSet& N = hsets[tr.src]; const HSet& M = hsets[tr.dst];
      double minHi = 1e300, maxLo = -1e300, uAt = 0, sAt = 0, uAt2 = 0, sAt2 = 0;
      vector<double> sg = grid(-N.b, N.b, probeK);
      vector<double> ug = grid(N.c - N.w, N.c + N.w, probeK);
      for (int side = 0; side < 4; ++side)
        for (int i = 0; i <= probeK; ++i) {
          double up = side == 0 ? N.c - N.w : side == 1 ? N.c + N.w : ug[i];
          double sp = side == 2 ? -N.b : side == 3 ? N.b : sg[i];
          I u, s;
          if (!imageInChart(fl, charts[N.chart], I(up), I(sp), charts[M.chart], u, s)) continue;
          if (s.rightBound() < minHi) { minHi = s.rightBound(); uAt = up; sAt = sp; }
          if (s.leftBound() > maxLo) { maxLo = s.leftBound(); uAt2 = up; sAt2 = sp; }
        }
      std::printf("probe %s->%s: min over boundary points of rightBound(s) = %.12g at (u,s)=(%.17g,%.17g)\n",
                  probeSrc.c_str(), probeDst.c_str(), minHi, uAt, sAt);
      std::printf("probe %s->%s: max over boundary points of leftBound(s)  = %.12g at (u,s)=(%.17g,%.17g)\n",
                  probeSrc.c_str(), probeDst.c_str(), maxLo, uAt2, sAt2);
      std::printf("probe: bM = %.17g -> %s\n", M.b,
                  (minHi < -M.b || maxLo > M.b) ? "CERTIFIED (S) VIOLATION at a single point" : "no certified point violation");
    }
    return 0;
  }

  // (D) disjointness
  int nPairs = 0, nSep = 0;
  for (size_t i = 0; i < hsets.size(); ++i)
    for (size_t j = i + 1; j < hsets.size(); ++j) {
      ++nPairs;
      if (separated(hsets[i], hsets[j])) ++nSep;
      else { all = false; std::printf("(D) FAIL: %s and %s not proven disjoint\n", hsets[i].name.c_str(), hsets[j].name.c_str()); }
    }
  std::printf("(D) disjointness: %d/%d pairs separated -> %s\n", nSep, nPairs, nSep == nPairs ? "OK" : "FAIL");

  const char* kn[3] = {"E-", "E+", "S "};
  for (size_t t = 0; t < transList.size(); ++t) {
    const Trans& tr = transList[t];
    auto ts = std::chrono::steady_clock::now();
    bool trOk = true;
    for (int k = 0; k < 3; ++k) {
      Result r = runCheck(fl, (Kind)k, tr, k == 2 ? nStrip : nEdge);
      if (r.ok)
        std::printf("  %-4s -> %-4s o=%+d  %s OK    boxes=%ld refined=%ld worst margin=%.3e\n",
                    hsets[tr.src].name.c_str(), hsets[tr.dst].name.c_str(), tr.o, kn[k], r.boxes, r.refined, r.worstMargin);
      else
        std::printf("  %-4s -> %-4s o=%+d  %s FAIL  boxes=%ld  %s\n",
                    hsets[tr.src].name.c_str(), hsets[tr.dst].name.c_str(), tr.o, kn[k], r.boxes, r.msg.c_str());
      trOk = trOk && r.ok;
    }
    double dt = std::chrono::duration<double>(std::chrono::steady_clock::now() - ts).count();
    std::printf("trans %s -> %s (o=%+d): %s  [%.2f s]\n", hsets[tr.src].name.c_str(), hsets[tr.dst].name.c_str(),
                tr.o, trOk ? "VERIFIED" : "FAILED", dt);
    std::fflush(stdout);
    all = all && trOk;
  }
  double total = std::chrono::duration<double>(std::chrono::steady_clock::now() - t0).count();
  std::printf("integrations=%ld integration failures/guard rejections=%ld  total time %.2f s\n",
              nIntegrations, nIntegrationFailures, total);
  std::printf("%s\n", all ? "ALL VERIFIED" : "NOT VERIFIED");
  return all ? 0 : 1;
}

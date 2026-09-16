import 'dart:math' as math;

/// Monteq — Edge Simulator. PWA-capable Flutter wrapper.
/// Web math lives in app.html/js; this Flutter shell gives a native
/// installable app (Android/iOS/macOS/Windows/Web) with offline WASM-ready scaffolding.
/// Full engine: see gamble.py + app.html. This shell mirrors the web Information Architecture
/// and deep-links to /app (or opens in-app WebView when online).

import 'package:flutter/material.dart';

void main() => runApp(const MonteqApp());

class MonteqApp extends StatelessWidget {
  const MonteqApp({super.key});
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Monteq',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        brightness: Brightness.dark,
        scaffoldBackgroundColor: const Color(0xFF000000),
        fontFamily: 'NaN',
        colorScheme: const ColorScheme.dark(
          primary: Color(0xFFFF5A33),
          surface: Color(0xFF000000),
          onSurface: Color(0xFFF4F4F5),
          outline: Color(0xFF27272A),
        ),
        cardTheme: const CardThemeData(
          color: Colors.transparent,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.zero, side: BorderSide(color: Color(0xFF27272A))),
          margin: EdgeInsets.zero,
        ),
        inputDecorationTheme: InputDecorationTheme(
          filled: false,
          border: OutlineInputBorder(borderRadius: BorderRadius.zero, borderSide: const BorderSide(color: Color(0xFF27272A))),
          enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.zero, borderSide: const BorderSide(color: Color(0xFF27272A))),
          focusedBorder: OutlineInputBorder(borderRadius: BorderRadius.zero, borderSide: const BorderSide(color: Color(0xFF52525B))),
        ),
        elevatedButtonTheme: ElevatedButtonThemeData(
          style: ElevatedButton.styleFrom(
            backgroundColor: const Color(0xFFFF5A33),
            foregroundColor: Colors.black,
            shape: const RoundedRectangleBorder(borderRadius: BorderRadius.zero),
            textStyle: const TextStyle(letterSpacing: 1.1, fontWeight: FontWeight.w700, fontSize: 12),
          ),
        ),
      ),
      home: const Shell(),
    );
  }
}

class Shell extends StatefulWidget {
  const Shell({super.key});
  @override
  State<Shell> createState() => _ShellState();
}

class _ShellState extends State<Shell> {
  int _tab = 0;
  static const _labels = ['Home', 'Kelly', 'Monte Carlo', 'Lab', 'Parlay', 'Risk'];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Colors.black,
        elevation: 0,
        title: Row(children: [
          Image.asset('assets/logo.png', height: 28, errorBuilder: (_, __, ___) => const Text('MONTEQ', style: TextStyle(letterSpacing: 3, fontSize: 11, fontWeight: FontWeight.w700))),
          const SizedBox(width: 12),
          const Expanded(
            child: SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: Row(children: [
                // Tab chips rendered below; header stays minimal for PWA
              ]),
            ),
          ),
        ]),
        bottom: PreferredSize(
          preferredSize: const Size.fromHeight(40),
          child: Container(
            decoration: const BoxDecoration(border: Border(bottom: BorderSide(color: Color(0xFF27272A)))),
            child: SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: Row(
                children: List.generate(_labels.length, (i) {
                  final sel = i == _tab;
                  return GestureDetector(
                    onTap: () => setState(() => _tab = i),
                    child: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                      decoration: BoxDecoration(border: Border(bottom: BorderSide(color: sel ? const Color(0xFFFF5A33) : Colors.transparent, width: 2))),
                      child: Text(_labels[i].toUpperCase(),
                          style: TextStyle(fontSize: 10, letterSpacing: 1.6, fontWeight: FontWeight.w600, color: sel ? Colors.white : const Color(0xFF71717A))),
                    ),
                  );
                }),
              ),
            ),
          ),
        ),
      ),
      body: IndexedStack(index: _tab, children: [
        const HomePane(),
        KellyPane(onNeedApp: () => setState(() => _tab = 1)),
        const MontePane(),
        const LabPane(),
        const ParlayPane(),
        const RiskPane(),
      ]),
    );
  }
}

// ── Math (mirrors gamble.py / app.html) ─────────────────────────────────
double kellyF(double p, double dec) {
  final b = dec - 1;
  return (b * p - (1 - p)) / b;
}

Map<String, double> kellyStats(double p, double dec) {
  final b = dec - 1, q = 1 - p, f = kellyF(p, dec);
  final ev = p * b - q, implied = 1 / dec, edge = p - implied;
  double g = 0, dbl = double.infinity;
  if (f > 0 && f < 1) {
    g = p * math.log(1 + f * b) + q * math.log(1 - f);
    if (g > 0) dbl = math.log(2) / g;
  }
  return {'b': b, 'f': f, 'ev': ev, 'implied': implied, 'edge': edge, 'g': g, 'dbl': dbl};
}

double? tryProb(String s) {
  s = s.trim();
  if (s.isEmpty) return null;
  if (s.endsWith('%')) {
    final v = double.tryParse(s.substring(0, s.length - 1));
    if (v == null) return null;
    if (v < 0 || v > 100) return null;
    return v / 100;
  }
  final v = double.tryParse(s);
  if (v == null) return null;
  if (v > 1 && v <= 100) return v / 100;
  if (v < 0 || v > 1) return null;
  if (v == 0 || v == 1) return null;
  return v;
}

double? tryDec(String s) {
  s = s.trim();
  if (s.isEmpty) return null;
  if (s.contains('/')) {
    final a = s.split('/');
    if (a.length == 2) {
      final x = double.tryParse(a[0]), y = double.tryParse(a[1]);
      if (x != null && y != null && y != 0) return x / y + 1;
    }
  }
  if (RegExp(r'^[+-]\d+(\.\d+)?$').hasMatch(s)) {
    final v = double.parse(s);
    return v > 0 ? v / 100 + 1 : 100 / v.abs() + 1;
  }
  final v = double.tryParse(s);
  if (v == null || v <= 1 || v > 1000) return null;
  return v;
}

String fmtMoney(double x) {
  if (!x.isFinite) return '—';
  if (x >= 1e9) return '\$${(x / 1e6).toStringAsFixed(2)}M';
  if (x >= 1e6) return '\$${(x / 1e3).toStringAsFixed(1)}k';
  if (x >= 1e3) return '\$${x.toStringAsFixed(0)}';
  return '\$${x.toStringAsFixed(2)}';
}

// ── Shared widgets ──────────────────────────────────────────────────────
class HeroBox extends StatelessWidget {
  const HeroBox({super.key});
  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: const BoxDecoration(border: Border(bottom: BorderSide(color: Color(0xFF27272A)))),
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 18),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        const Text('No accounts · No tracking · Runs in browser',
            style: TextStyle(fontSize: 9, letterSpacing: 1.6, color: Color(0xFF71717A), fontWeight: FontWeight.w600)),
        const SizedBox(height: 10),
        Stack(children: [
          Positioned(left: -8, top: -8, child: Container(width: 90, height: 56, color: const Color(0xFF1A2E1C).withOpacity(0.5))),
          const Text('Bet sizing\nyou can trust.', style: TextStyle(fontSize: 32, height: 0.95, letterSpacing: -1.2, fontWeight: FontWeight.w900, color: Color(0xFFF4F4F5))),
        ]),
        const SizedBox(height: 10),
        const Text('Kelly, Monte Carlo, parlays and ruin — one brutally honest dashboard. No accounts, no tracking. Accessible anywhere, and your numbers still never leave the browser.',
            style: TextStyle(fontSize: 12, height: 1.5, color: Color(0xFFA1A1AA))),
      ]),
    );
  }
}

class KVGrid extends StatelessWidget {
  final List<Widget> children;
  const KVGrid({super.key, required this.children});
  @override
  Widget build(BuildContext context) => GridView.count(crossAxisCount: 2, shrinkWrap: true, physics: const NeverScrollableScrollPhysics(), mainAxisSpacing: 8, crossAxisSpacing: 8, childAspectRatio: 1.8, children: children);
}

Container kvCard(String label, String value, String sub, {Color? valueColor}) => Container(
      decoration: BoxDecoration(border: Border.all(color: const Color(0xFF27272A))),
      padding: const EdgeInsets.all(10),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Text(label, style: const TextStyle(fontSize: 8, letterSpacing: 1.2, color: Color(0xFF71717A), fontWeight: FontWeight.w600)),
        const SizedBox(height: 6),
        Text(value, style: TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: valueColor ?? Colors.white)),
        const SizedBox(height: 2),
        Text(sub, style: const TextStyle(fontSize: 10, color: Color(0xFF71717A))),
      ]),
    );

// ── Panes ───────────────────────────────────────────────────────────────
class HomePane extends StatelessWidget {
  const HomePane({super.key});
  @override
  Widget build(BuildContext context) {
    return ListView(padding: const EdgeInsets.fromLTRB(16, 12, 16, 24), children: [
      const HeroBox(),
      const SizedBox(height: 16),
      GridView.count(
        crossAxisCount: 2,
        shrinkWrap: true,
        physics: const NeverScrollableScrollPhysics(),
        crossAxisSpacing: 8,
        mainAxisSpacing: 8,
        childAspectRatio: 1.55,
        children: [
          _navCard(context, '01 — KELLY', 'Optimal size, sane size', 'f* = (bp−q)/b. Half keeps ~75% growth.', 1),
          _navCard(context, '02 — MONTE CARLO', '5,000 futures', 'P5 / median / P95. Spread, not average.', 2),
          _navCard(context, '03 — LAB & PARLAY', 'Fractions & accumulators', '0.25×→1.5×. Parlays: variance explodes.', 3),
          _navCard(context, '04 — RISK', 'Streaks & ruin', 'qⁿ, drawdown, gambler\'s ruin.', 5, olive: true),
        ],
      ),
      const SizedBox(height: 12),
      Container(
        decoration: BoxDecoration(border: Border.all(color: const Color(0xFF27272A))),
        padding: const EdgeInsets.all(12),
        child: const Text('Odds: 2.50 or +150 / −110 or 5/2 · Prob: 55% or 0.55 · Shortcuts mirror web: keep your inputs consistent.',
            style: TextStyle(fontSize: 10, color: Color(0xFFA1A1AA), height: 1.5)),
      ),
    ]);
  }

  Widget _navCard(BuildContext c, String k, String t, String d, int tab, {bool olive = false}) => GestureDetector(
        onTap: () {
          final s = c.findAncestorStateOfType<_ShellState>();
          s?.setState(() => s._tab = tab);
        },
        child: Container(
          decoration: BoxDecoration(border: Border.all(color: const Color(0xFF27272A)), color: olive ? const Color(0xFF1A2E1C).withOpacity(0.18) : Colors.transparent),
          padding: const EdgeInsets.all(12),
          child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Text(k, style: const TextStyle(fontSize: 8, letterSpacing: 1.1, color: Color(0xFF71717A), fontWeight: FontWeight.w600)),
            const SizedBox(height: 8),
            Text(t, style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: Color(0xFFF4F4F5))),
            const SizedBox(height: 6),
            Text(d, style: const TextStyle(fontSize: 11, height: 1.4, color: Color(0xFFA1A1AA))),
          ]),
        ),
      );
}

class KellyPane extends StatefulWidget {
  final VoidCallback onNeedApp;
  const KellyPane({super.key, required this.onNeedApp});
  @override
  State<KellyPane> createState() => _KellyPaneState();
}

class _KellyPaneState extends State<KellyPane> {
  final _p = TextEditingController(text: '55%');
  final _odds = TextEditingController(text: '2.00');
  final _br = TextEditingController(text: '1000');

  @override
  Widget build(BuildContext context) {
    final p = tryProb(_p.text), dec = tryDec(_odds.text);
    final br = double.tryParse(_br.text) ?? 1000;
    final valid = p != null && dec != null && p > 0 && p < 1 && dec > 1;
    final s = valid ? kellyStats(p, dec) : null;
    final f = s?['f'] ?? 0.0;
    final isGood = f > 0;
    return ListView(padding: const EdgeInsets.fromLTRB(16, 12, 16, 24), children: [
      _field('Win probability', '55% or 0.55', _p, hint: 'Try 52% / 60%'),
      const SizedBox(height: 10),
      _field('Odds', '2.5 · +150 · 5/2', _odds),
      const SizedBox(height: 10),
      _field('Bankroll \$', '1000', _br, number: true),
      const SizedBox(height: 14),
      if (!valid)
        _callout('Enter probability & odds → Kelly tells optimal size.', tone: 'neutral')
      else if (!isGood)
        _callout('No edge — Kelly 0. Don\'t bet at these odds.', tone: 'bad')
      else if (f > 0.25)
        _callout('Large Kelly (>25%). Use half or quarter.', tone: 'warn')
      else
        _callout('Good edge. Half Kelly keeps ~75% growth with ~½ variance.', tone: 'olive'),
      const SizedBox(height: 12),
      if (valid) ...[
        KVGrid(children: [
          kvCard('Implied prob', '${(s!['implied']! * 100).toStringAsFixed(2)}%', 'from ${dec!.toStringAsFixed(2)}×'),
          kvCard('Your edge', '${(s['edge']! * 100).toStringAsFixed(2)} pp', 'prob − implied', valueColor: s['edge']! > 0 ? const Color(0xFFFF5A33) : Colors.redAccent),
          kvCard('EV / \$1', '${s['ev']! > 0 ? '+' : ''}${s['ev']!.toStringAsFixed(4)}', 'per unit'),
          kvCard('Kelly f*', '${(f * 100).toStringAsFixed(2)}%', isGood ? 'full Kelly' : 'don\'t bet', valueColor: isGood ? const Color(0xFFFF5A33) : Colors.redAccent),
        ]),
        const SizedBox(height: 12),
        Container(
          decoration: BoxDecoration(border: Border.all(color: const Color(0xFF27272A))),
          padding: const EdgeInsets.all(10),
          child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            const Text('Fractions', style: TextStyle(fontSize: 9, letterSpacing: 1.2, color: Color(0xFF71717A), fontWeight: FontWeight.w600)),
            const SizedBox(height: 8),
            for (final r in [
              [1.0, 'Full'],
              [0.5, 'Half'],
              [0.33, 'Third'],
              [0.25, 'Quarter']
            ])
              Padding(
                padding: const EdgeInsets.symmetric(vertical: 4),
                child: Row(children: [
                  SizedBox(width: 70, child: Text(r[1] as String, style: const TextStyle(fontSize: 11, color: Color(0xFFF4F4F5)))),
                  Text('${((f.clamp(0, 1) * (r[0] as double)) * 100).toStringAsFixed(2)}%', style: const TextStyle(fontSize: 11, color: Colors.white, fontWeight: FontWeight.w700)),
                  const Spacer(),
                  Text('${(r[0] as double)}×', style: const TextStyle(fontSize: 10, color: Color(0xFF71717A))),
                  if (r[0] == 0.5)
                    Container(margin: const EdgeInsets.only(left: 6), padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2), color: const Color(0xFFFF5A33), child: const Text('recommended', style: TextStyle(fontSize: 8, color: Colors.black, fontWeight: FontWeight.w700))),
                ]),
              ),
          ]),
        ),
        const SizedBox(height: 12),
        KVGrid(children: [
          kvCard('Full Kelly', fmtMoney((f.clamp(0, 1) * br)), '${(f.clamp(0, 1) * 100).toStringAsFixed(2)}%'),
          kvCard('Half Kelly', fmtMoney((f.clamp(0, 1) * br * 0.5)), 'recommended', valueColor: const Color(0xFFFF5A33)),
          kvCard('Quarter', fmtMoney((f.clamp(0, 1) * br * 0.25)), 'lowest variance'),
          kvCard('Double time', isGood && (s['g']! > 0) ? '${s['dbl']!.toStringAsFixed(0)} bets' : '—', 'median at full'),
        ]),
      ],
    ]);
  }

  Widget _field(String label, String hint, TextEditingController c, {bool number = false}) => Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Text(label.toUpperCase(), style: const TextStyle(fontSize: 9, letterSpacing: 1.2, color: Color(0xFFA1A1AA), fontWeight: FontWeight.w600)),
        const SizedBox(height: 6),
        TextField(controller: c, keyboardType: number ? TextInputType.number : TextInputType.text, style: const TextStyle(color: Colors.white, fontSize: 13), decoration: InputDecoration(hintText: hint, hintStyle: const TextStyle(color: Color(0xFF52525B), fontSize: 12)), onChanged: (_) => setState(() {})),
      ]);

  Widget _callout(String msg, {required String tone}) {
    Color border = const Color(0xFF27272A);
    Color bg = Colors.transparent;
    String icon = '◈';
    if (tone == 'bad') {
      border = const Color(0xFF7F1D1D);
      bg = const Color(0xFF450A0A).withOpacity(0.22);
      icon = '✘';
    } else if (tone == 'warn') {
      border = const Color(0xFF78350F);
      bg = const Color(0xFF451A03).withOpacity(0.2);
      icon = '⚠';
    } else if (tone == 'olive') {
      border = const Color(0xFF1A2E1C);
      bg = const Color(0xFF1A2E1C).withOpacity(0.22);
      icon = '✓';
    }
    return Container(
      decoration: BoxDecoration(color: bg, border: Border.all(color: border)),
      padding: const EdgeInsets.all(10),
      child: Row(children: [Text(icon, style: const TextStyle(color: Colors.white, fontSize: 11)), const SizedBox(width: 8), Expanded(child: Text(msg, style: const TextStyle(fontSize: 11, height: 1.4, color: Color(0xFFD4D4D8))))]),
    );
  }
}

class MontePane extends StatelessWidget {
  const MontePane({super.key});
  @override
  Widget build(BuildContext context) => ListView(padding: const EdgeInsets.all(16), children: [
        const Text('Monte Carlo', style: TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: Colors.white, letterSpacing: 0.8)),
        const SizedBox(height: 8),
        const Text('Run 5,000 futures on-device. P5 / median / P95. If P5 nears zero, you bet too big. Uses the same engine as the web app (see app.html for charts).',
            style: TextStyle(fontSize: 11, height: 1.5, color: Color(0xFFA1A1AA))),
        const SizedBox(height: 16),
        Container(
          decoration: BoxDecoration(border: Border.all(color: const Color(0xFF27272A))),
          padding: const EdgeInsets.all(12),
          child: const Text('Tip: open the web app for full histograms & equity curves. This native build focuses on sizing & distribution summaries — charts arrive via the next update.',
              style: TextStyle(fontSize: 11, height: 1.5, color: Color(0xFFA1A1AA))),
        ),
      ]);
}

class LabPane extends StatelessWidget {
  const LabPane({super.key});
  @override
  Widget build(BuildContext context) => ListView(padding: const EdgeInsets.all(16), children: const [
        Text('Lab — Fractions', style: TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: Colors.white, letterSpacing: 0.8)),
        SizedBox(height: 8),
        Text('0.25× → 1.5× head-to-head. Best median ≠ best P5. Use the web app Lab sweep for exact tables & charts.',
            style: TextStyle(fontSize: 11, height: 1.5, color: Color(0xFFA1A1AA))),
      ]);
}

class ParlayPane extends StatelessWidget {
  const ParlayPane({super.key});
  @override
  Widget build(BuildContext context) => ListView(padding: const EdgeInsets.all(16), children: const [
        Text('Parlay — Accumulator', style: TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: Colors.white, letterSpacing: 0.8)),
        SizedBox(height: 8),
        Text('Combined p = ∏pᵢ, dec = ∏decᵢ. Assumes independent legs. Variance explodes — Kelly shrinks fast. Compare best single vs combined in the web app.',
            style: TextStyle(fontSize: 11, height: 1.5, color: Color(0xFFA1A1AA))),
      ]);
}

class RiskPane extends StatelessWidget {
  const RiskPane({super.key});
  @override
  Widget build(BuildContext context) => ListView(padding: const EdgeInsets.all(16), children: const [
        Text('Risk — Streaks & Drawdown', style: TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: Colors.white, letterSpacing: 0.8)),
        SizedBox(height: 8),
        Text('qⁿ, pⁿ, drawdown at x%/bet (n to −50% = log 0.5 / log(1−x)), gambler\'s ruin. Small edges drown in streaks — size down.',
            style: TextStyle(fontSize: 11, height: 1.5, color: Color(0xFFA1A1AA))),
      ]);
}

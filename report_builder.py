import html
from datetime import datetime
from pathlib import Path

CSS = """
:root{--pass:#16a34a;--fail:#dc2626;--skip:#9ca3af;--bg:#f3f4f6;--ink:#111827}
*{box-sizing:border-box}
body{margin:0;font-family:Segoe UI,system-ui,sans-serif;background:var(--bg);color:var(--ink)}
header{background:linear-gradient(135deg,#0f172a,#1e40af);color:#fff;padding:28px 40px}
header h1{margin:0 0 4px;font-size:26px}header p{margin:0;opacity:.8}
main{max-width:1200px;margin:0 auto;padding:24px}
.cards{display:flex;gap:16px;flex-wrap:wrap;margin:-48px 0 24px}
.card{flex:1;min-width:150px;background:#fff;border-radius:12px;padding:16px 20px;box-shadow:0 2px 8px #0002}
.card b{display:block;font-size:30px}.card span{color:#6b7280;font-size:13px;text-transform:uppercase}
.card.pass b{color:var(--pass)}.card.fail b{color:var(--fail)}
.bar{height:10px;border-radius:5px;background:var(--fail);overflow:hidden;margin:8px 0 20px}
.bar div{height:100%;background:var(--pass)}
.filters{margin-bottom:16px}.filters button{border:0;background:#fff;padding:8px 16px;border-radius:20px;margin-right:8px;cursor:pointer;box-shadow:0 1px 3px #0002}
.filters button.on{background:#1e40af;color:#fff}
details.sc{background:#fff;border-radius:12px;margin-bottom:12px;box-shadow:0 1px 4px #0002;border-left:6px solid var(--skip)}
details.sc.passed{border-color:var(--pass)}details.sc.failed,details.sc.error{border-color:var(--fail)}
summary{padding:14px 18px;cursor:pointer;display:flex;align-items:center;gap:12px;font-weight:600}
.badge{font-size:12px;padding:3px 10px;border-radius:12px;color:#fff;background:var(--skip);text-transform:uppercase}
.badge.passed{background:var(--pass)}.badge.failed,.badge.error{background:var(--fail)}
.tag{font-size:12px;color:#1e40af;background:#dbeafe;padding:2px 8px;border-radius:10px;font-weight:400}
.time{margin-left:auto;color:#6b7280;font-weight:400;font-size:13px}
.steps{padding:4px 18px 18px}
.step{display:flex;gap:16px;padding:12px 0;border-top:1px solid #e5e7eb;align-items:flex-start}
.step .txt{flex:1}.step .kw{font-weight:700;color:#1e40af}
.step small{color:#6b7280;margin-left:8px}
pre{background:#fef2f2;color:#991b1b;padding:10px;border-radius:8px;white-space:pre-wrap;font-size:12px}
.shot{width:220px;border-radius:8px;border:1px solid #d1d5db;cursor:zoom-in;transition:.15s}
.shot:hover{box-shadow:0 4px 12px #0004}
#lb{display:none;position:fixed;inset:0;background:#000d;align-items:center;justify-content:center;z-index:9;cursor:zoom-out}
#lb img{max-width:94vw;max-height:94vh;border-radius:8px}
"""

JS = """
function filt(s,b){document.querySelectorAll('.filters button').forEach(x=>x.classList.remove('on'));b.classList.add('on');
document.querySelectorAll('details.sc').forEach(d=>{d.style.display=(s==='all'||d.classList.contains(s))?'':'none'})}
function zoom(i){var l=document.getElementById('lb');l.firstChild.src=i.src;l.style.display='flex'}
document.getElementById('lb').onclick=function(){this.style.display='none'}
"""


class Report:
    def __init__(self, base_url: str = ""):
        self.started = datetime.now()
        self.base_url = base_url
        self.tests = []

    def add_test(self, name, steps, tags, status, duration, error, screenshot_b64):
        self.tests.append(
            {
                "name": name,
                "steps": steps,
                "tags": tags,
                "status": status,
                "duration": duration,
                "error": error,
                "shot": screenshot_b64,
            }
        )

    def write(self, path: Path) -> None:
        total = len(self.tests)
        passed = sum(t["status"] == "passed" for t in self.tests)
        failed = total - passed
        duration = sum(t["duration"] for t in self.tests)
        pct = round(100 * passed / total) if total else 0

        parts = [
            f"<!doctype html><meta charset='utf-8'><title>ICS Cards test report</title><style>{CSS}</style>",
            "<header><h1>ICS Cards - Playwright + pytest report</h1>",
            f"<p>{self.started:%d %b %Y %H:%M} &middot; {html.escape(self.base_url)}</p></header><main>",
            "<div class='cards'>",
            f"<div class='card'><span>Tests</span><b>{total}</b></div>",
            f"<div class='card pass'><span>Passed</span><b>{passed}</b></div>",
            f"<div class='card fail'><span>Failed</span><b>{failed}</b></div>",
            f"<div class='card'><span>Duration</span><b>{duration:.0f}s</b></div></div>",
            f"<div class='bar'><div style='width:{pct}%'></div></div>",
            "<div class='filters'><button class='on' onclick=\"filt('all',this)\">All</button>"
            "<button onclick=\"filt('passed',this)\">Passed</button>"
            "<button onclick=\"filt('failed',this)\">Failed</button></div>",
        ]
        for t in self.tests:
            status = t["status"]
            css = "failed" if status in ("failed", "error") else status
            tags = "".join(f"<span class='tag'>@{html.escape(tag)}</span>" for tag in t["tags"])
            img = f"<img class='shot' onclick='zoom(this)' src='data:image/png;base64,{t['shot']}'>" if t["shot"] else ""
            err = f"<pre>{html.escape(t['error'])}</pre>" if t["error"] else ""
            steps = "".join(
                f"<div><span class='kw'>{html.escape(s.split(' ', 1)[0])}</span> {html.escape(s.split(' ', 1)[-1])}</div>"
                for s in t["steps"]
            )
            parts.append(
                f"<details class='sc {css}'><summary><span class='badge {css}'>{status}</span>"
                f"{html.escape(t['name'])} {tags}<span class='time'>{t['duration']:.1f}s</span></summary>"
                f"<div class='steps'><div class='step'><div class='txt'>"
                f"{steps}{err}</div>{img}</div></div></details>"
            )
        parts.append(f"</main><div id='lb'><img></div><script>{JS}</script>")
        path.write_text("".join(parts), encoding="utf-8")

"""Make a local Windows-friendly native review gallery from the private CI artifact ZIP.

The original ZIP retains the complete xcresult. Only named review PNGs and small
JSON evidence are copied, avoiding Windows path limits in xcresult internals.
No server, credentials, image transformation or application commands are used.
"""
import argparse
import html
import hashlib
import json
from pathlib import Path
import re
import shutil
import zipfile

REFERENCES = {
    'wake': '04-wake', 'still-fallback': '05-still', 'still-artwork': '05-still',
    'touched': '06-touched', 'first-contact': '06-touched', 'queue': '07-river',
    'ask-recording': '08-ask', 'ask-stopped': '08-ask', 'paused': '10-paused',
    'stopped': '11-stopped', 'offline': '12-offline', 'pending': '13-pending',
    'unknown': '14-unknown', 'longtitle': '15-longtitle', 'noart': '16-noart',
    'find': '17-find', 'after-search': '17-find', 'keyboard': '18-keyboard', 'detail': '19-detail',
    'library': '20-library', 'settings': '21-settings', 'display': '22-display',
}


def build(archive, output, revision=None):
    if revision is not None and not re.fullmatch(r'[0-9a-f]{40}', revision):
        raise ValueError('Use the full source commit SHA shown on the GitHub run.')
    output.mkdir(parents=True, exist_ok=True)
    states = []
    with zipfile.ZipFile(archive) as source:
        def read(name, limit):
            item = source.getinfo(name)
            if item.file_size > limit:
                raise ValueError(f'Oversized evidence file: {name}')
            return source.read(item)

        summary = json.loads(read('test-summary.json', 1024 * 1024))
        environment = json.loads(read('environment.json', 1024 * 1024))
        manifest = json.loads(read('screenshots/manifest.json', 4 * 1024 * 1024))
        for group in manifest:
            for attachment in reversed(group['attachments']):
                name = attachment['suggestedHumanReadableName']
                match = re.match(r'^StillWater-([a-z-]+)-1510x692_', name)
                state = match[1] if match else 'keyboard' if name.startswith('Find-system-keyboard_') else (
                    'first-contact' if name.startswith('First-contact-touched_') else
                    'after-search' if name.startswith('Find-after-search_') else None)
                if not state:
                    continue
                exported = attachment['exportedFileName']
                if not re.fullmatch(r'[A-Za-z0-9-]+\.png', exported):
                    raise ValueError('Unexpected screenshot filename')
                (output / (state + '.png')).write_bytes(read('screenshots/' + exported, 16 * 1024 * 1024))
                if state not in states:
                    states.append(state)
        for name, value in [('test-summary', summary), ('environment', environment)]:
            (output / (name + '.json')).write_text(json.dumps(value, indent=2) + '\n', encoding='utf-8')
    if not states:
        raise ValueError('No native review captures found; inspect the failed build log.')
    with archive.open('rb') as stream:
        archive_digest = hashlib.file_digest(stream, 'sha256').hexdigest()
    provenance = {'archive_sha256': archive_digest, 'source_commit_from_run': revision}
    (output / 'provenance.json').write_text(json.dumps(provenance, indent=2) + '\n', encoding='utf-8')
    reference_root = Path(__file__).resolve().parents[1] / 'docs/still-water/reference'
    references = {}
    for state in states:
        stem = REFERENCES.get(state)
        if stem and (reference_root / (stem + '.png')).is_file():
            name = 'reference-' + stem + '.png'
            shutil.copyfile(reference_root / (stem + '.png'), output / name)
            references[state] = name
    evidence = html.escape(f"{summary['result']}: {summary['passedTests']}/{summary['totalTestCount']} tests passed. "
                           + environment['xcode'].replace('\n', ' · '))
    if revision:
        evidence += ' · Source ' + revision
    options = ''.join(f'<option value="{s}">{s}</option>' for s in states)
    page = '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>Still Water — native simulator review</title><style>
*{box-sizing:border-box}body{margin:0;padding:28px;background:#101412;color:#eeeade;font:16px system-ui}
h1{font:36px Georgia;margin:0 0 10px}p{max-width:1000px;line-height:1.5;color:#bac3b9}
nav{display:flex;gap:16px;align-items:center;flex-wrap:wrap;margin:24px 0}select,button{font:inherit;padding:10px;background:#26332b;color:#eeeade;border:1px solid #607463;border-radius:6px}
section{margin:24px 0}h2{font-size:18px}figure{margin:0;overflow:auto;border:1px solid #354037;background:#000;padding:8px}
img{display:block;width:min(100%,1510px);height:auto}body.full img{width:auto;max-width:none}a{color:#d8c49a}small{color:#bac3b9}
</style><h1>Still Water · native simulator review</h1>
<p>__EVIDENCE__</p><p>Actual iPhone 11 simulator captures. This page reviews screenshots; it does not run the app or send commands. The original reference is 800 × 480; native layout follows the 1048 × 480 anchored tables and documented D031 exceptions. Physical and user acceptance remain separate.</p>
<nav><button id="prev">Previous</button><label>State <select id="state">__OPTIONS__</select></label><button id="next">Next</button><label><input type="checkbox" id="full"> Full pixel size</label><a href="test-summary.json">Test evidence</a><a href="environment.json">Build environment</a><a href="provenance.json">Artifact identity</a></nav>
<section><h2 id="caption"></h2><figure><img id="native" alt="Native simulator screenshot"></figure></section>
<section id="reference-block"><h2>Original design reference</h2><p>Compare hierarchy, type, spacing and state feedback. Do not stretch this narrower reference to match the native canvas.</p><figure><img id="reference" alt="Original supplied design reference" style="max-width:800px"></figure></section>
<p id="extra" hidden>Additional native utility screen; no matching supplied render.</p>
<script>const references=__REFERENCES__;const picker=document.querySelector('#state');
function show(){const name=picker.value;document.querySelector('#native').src=name+'.png';document.querySelector('#caption').textContent='Native · '+name;const ref=references[name];document.querySelector('#reference-block').hidden=!ref;document.querySelector('#extra').hidden=!!ref;if(ref)document.querySelector('#reference').src=ref;}
picker.onchange=show;document.querySelector('#prev').onclick=()=>{picker.selectedIndex=(picker.selectedIndex+picker.length-1)%picker.length;show()};document.querySelector('#next').onclick=()=>{picker.selectedIndex=(picker.selectedIndex+1)%picker.length;show()};document.querySelector('#full').onchange=e=>document.body.classList.toggle('full',e.target.checked);show();</script></html>'''
    page = page.replace('__EVIDENCE__', evidence).replace('__OPTIONS__', options).replace('__REFERENCES__', json.dumps(references))
    (output / 'review.html').write_text(page, encoding='utf-8')
    print(f'{len(states)} native captures: {(output / "review.html").resolve()}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', type=Path)
    parser.add_argument('--output', type=Path, default=Path('local/ios/review'))
    parser.add_argument('--revision', help='Full commit SHA from the matching GitHub run')
    args = parser.parse_args()
    build(args.archive, args.output, args.revision)

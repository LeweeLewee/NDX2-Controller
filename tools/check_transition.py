"""Explicit live test: replaces playback, seeks near a track end, then stops.

Device state can prove a transition, not audible gaplessness.
"""
import argparse
import datetime
import json
import pathlib
import time

from naim_client import NaimClient, playback_state

FIELDS = ('title', 'transportState', 'transportPosition', 'duration', 'source', 'sourceDetail', 'codec', 'bitDepth', 'sampleRate', 'error')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('address')
    parser.add_argument('album', help='Native album reference returned by NDX')
    parser.add_argument('--replace-playback', action='store_true', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    target = pathlib.Path(args.output)
    # Reserve the report before any live mutation; never overwrite evidence.
    with target.open('x', encoding='utf-8') as report_file:
        client = NaimClient(args.address)
        report = {'date': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'samples': [], 'gapless': 'not audibly verified'}

        def sample(label):
            data = client.status()
            row = {'label': label, **{k: data[k] for k in FIELDS if k in data}}
            report['samples'].append(row)
            print(json.dumps(row), flush=True)
            return data

        attempted = False
        try:
            sample('before')
            description = client.browse(args.album)
            if len(description.get('children', [])) < 2:
                raise ValueError('Need an album with two or more tracks')
            attempted = True
            client.play(args.album)
            deadline = time.monotonic() + 20
            while True:
                time.sleep(2)
                first = sample('startup')
                if playback_state(first) == 'playing' and int(first.get('duration', 0)) > 20000:
                    break
                if time.monotonic() > deadline:
                    raise TimeoutError('Playback did not become ready')
            client.transport('seek', int(first['duration']) - 12000)
            for n in range(10):
                time.sleep(2)
                sample('boundary-' + str(n))
            # New client and connection; no device or LAN outage induced.
            client = NaimClient(args.address)
            sample('fresh-client')
            time.sleep(3)
            sample('fresh-client-advancing')
        except Exception as exc:
            report['failure'] = type(exc).__name__
            raise
        finally:
            if attempted:
                try:
                    client.transport('stop')
                    time.sleep(3)
                    final = sample('final-after-stop')
                    report['stop_confirmed'] = playback_state(final) == 'stopped'
                except Exception as exc:
                    report['cleanup_failure'] = type(exc).__name__
            json.dump(report, report_file, indent=2)


if __name__ == '__main__':
    main()

"""800 x 480 native desktop fixture harness (Tk), not ESP32 browser firmware."""
import argparse
import getpass
import tkinter as tk
import threading
from tkinter import simpledialog
from m2_client import Client, Controller
from m2_security import Vault

CHARCOAL, SAGE, SAND = '#242925', '#adbaa7', '#ded4bd'


class Window:
    def __init__(self, model):
        self.model = model
        self.ui_busy = False
        self.root = tk.Tk(); self.root.title('NDX2 — SILENT M2 FIXTURE')
        self.root.geometry('800x480'); self.root.resizable(False, False)
        self.root.configure(bg=CHARCOAL)
        self.note = tk.StringVar(value='SILENT FIXTURE • no physical audio or microphone')
        self.root.bind('<ButtonRelease-1>', lambda e: self.model.touch(False))
        self.model.reconnect()
        self.render(); self.root.after(1000, self.poll)

    def button(self, parent, text, command, enabled=True):
        def invoke():
            if self.model.wake_contact or self.ui_busy: return
            try: command()
            except Exception: self.note.set('Unavailable — reconnect; no commands replayed')
            self.render()
        button = tk.Button(parent, text=text, command=invoke, bg=SAGE, fg=CHARCOAL,
                           font=('Arial', 14), relief='flat', padx=8, pady=10,
                           state='normal' if enabled else 'disabled', wraplength=600)
        return button

    def render(self):
        for child in self.root.winfo_children(): child.destroy()
        top = tk.Frame(self.root, bg=CHARCOAL, height=56); top.pack(fill='x'); top.pack_propagate(False)
        self.button(top, 'Back', self.model.back).pack(side='left')
        status = 'busy' if self.ui_busy else 'fresh' if self.model.available else 'stale / unavailable'
        self.status = tk.Label(top, text='SILENT FIXTURE  •  ' + status, bg=CHARCOAL, fg=SAND, font=('Arial', 17))
        self.status.pack(side='left', padx=8)
        self.button(top, 'Wake', self.model.wake).pack(side='right')
        bottom = tk.Frame(self.root, bg=CHARCOAL, height=64); bottom.pack(side='bottom', fill='x')
        for title, page in [('Now Playing', 'now'), ('Find', 'find'), ('Collection', 'collection'), ('Queue', 'queue'), ('Voice', 'voice')]:
            self.button(bottom, title, lambda p=page: self.model.push(p)).pack(side='left', expand=True, fill='x', padx=4)
        tk.Label(self.root, textvariable=self.note, bg=CHARCOAL, fg=SAND, font=('Arial', 11)).pack(side='bottom')
        body = tk.Frame(self.root, bg=CHARCOAL); body.pack(fill='both', expand=True, padx=12, pady=6)
        screen = self.model.context['screen']
        def label(text):
            tk.Label(body, text=text, bg=CHARCOAL, fg=SAND, font=('Arial', 20),
                     wraplength=750, justify='left').pack(anchor='w', pady=6)
        if screen == 'now':
            player = (self.model.snapshot or {}).get('player', {})
            label(player.get('title', 'Reconnect for authoritative state'))
            label(player.get('artist', ''))
            label('Artwork unavailable • battery unknown (hardware pending)')
            row = tk.Frame(body, bg=CHARCOAL); row.pack(fill='x')
            for title, action, args in [('Pause', 'transport', {'command':'pause'}),
                                         ('Amp −', 'amplifier', {'direction':'down'}),
                                         ('Amp +', 'amplifier', {'direction':'up'})]:
                self.button(row, title, lambda a=action, b=args: self.mutation(a,b), self.model.available and not self.ui_busy).pack(side='left', padx=8)
        elif screen == 'find':
            row = tk.Frame(body, bg=CHARCOAL); row.pack(fill='x')
            query = tk.Entry(row, font=('Arial', 20), bg=SAND); query.insert(0, self.model.context['query'])
            query.pack(side='left', fill='x', expand=True)
            self.button(row, 'Search albums', lambda: self.model.search(query.get())).pack(side='right')
            canvas = tk.Canvas(body, bg=CHARCOAL, highlightthickness=0)
            scroll = tk.Scrollbar(body, command=canvas.yview); scroll.pack(side='right', fill='y')
            canvas.configure(yscrollcommand=scroll.set); canvas.pack(fill='both', expand=True)
            rows = tk.Frame(canvas, bg=CHARCOAL); canvas.create_window(0,0,window=rows, anchor='nw', width=745)
            def detail(item):
                self.model.context['scroll'] = canvas.yview()[0]
                self.model.details(item)
            for item in self.model.context['items']:
                text = item['title'] + '  •  ' + item.get('saved','unknown')
                self.button(rows, text, lambda i=item: detail(i)).pack(fill='x', pady=4)
            self.button(rows, 'More', self.model.more).pack(fill='x')
            rows.update_idletasks(); canvas.configure(scrollregion=canvas.bbox('all'))
            canvas.yview_moveto(self.model.context['scroll'])
        elif screen == 'details':
            item = self.model.selected['item']; label(item['title']); label('Artwork unavailable')
            self.button(body, 'Play now (native resolution)', lambda: self.mutation('play', {'reference':item['reference']}),
                        self.model.available and not self.ui_busy and self.model.selected['playable']).pack(side='left', padx=4)
            self.button(body, 'Check saved', lambda: self.saved(item)).pack(side='left', padx=4)
        elif screen == 'queue':
            for item in (self.model.snapshot or {}).get('queue', []): label(item['title'])
            label('Queue view only • refreshes from the bridge')
        elif screen == 'collection':
            label('Saved / unsaved / unknown')
            label('Open an album and Check saved. Failed reads stay unknown.')
        elif screen == 'voice':
            label('Voice: ' + self.model.voice + ' • fixture only')
            label(self.model.transcript or 'Physical capture pending microphone and pin selection')
            row = tk.Frame(body,bg=CHARCOAL); row.pack(fill='x')
            for title, fn in [('Stop & search', self.model.submit_voice), ('Restart', self.model.record),
                               ('Cancel', self.model.back)]:
                self.button(row, title, fn).pack(side='left', padx=4)

    def saved(self, item):
        state = self.model.read('library_state', {'reference':item['reference']})['saved_state']
        self.note.set('Collection: ' + state)
        intent = simpledialog.askstring('Fixture collection', 'Type save or remove to explicitly change this fixture:')
        if intent in ('save', 'remove'):
            self.mutation('library_save', {'reference':item['reference'], 'saved':intent == 'save'})

    def mutation(self, action, args):
        if self.ui_busy or not self.model.available: return
        self.ui_busy = True
        self.note.set('Busy — both amplifier controls disabled')
        self.render()
        result = []
        def work(): result.append(self.model.mutate(action,args))
        worker = threading.Thread(target=work, daemon=True); worker.start()
        def finish():
            if worker.is_alive(): self.root.after(25, finish); return
            self.ui_busy = False
            self.note.set('Command outcome: ' + str(result[0] if result else 'unknown') + ' • state reconciled')
            if action == 'play': self.model.push('now')
            self.render()
        self.root.after(25, finish)

    def poll(self):
        try:
            self.model.tick()
            if not self.ui_busy and not self.model.busy and self.model.clock() >= self.model.retry_at: self.model.reconnect()
            self.model.retry_at = max(self.model.retry_at, self.model.clock() + 2)
        except Exception: self.model.disconnect()
        self.status.configure(text='SILENT FIXTURE  •  ' + ('busy' if self.ui_busy else 'fresh' if self.model.available else 'stale / unavailable'))
        # Avoid destroying active typing/scrolling controls on each poll.
        self.root.after(1000, self.poll)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', default='https://127.0.0.1:8991')
    parser.add_argument('--trust', default='local/m2/tls/trust.pem')
    parser.add_argument('--state', default='local/m2/controller')
    args = parser.parse_args()
    vault = Vault(args.state)
    client = Client(args.url, args.trust, vault.data.get('controller', {}).get('credential'))
    if not client.credential:
        result = client.pair(getpass.getpass('Setup code from local bridge console: '))
        vault.update(lambda d: d.update(controller=result))
    window = Window(Controller(client))
    try: window.root.mainloop()
    finally: vault.close()


if __name__ == '__main__': main()

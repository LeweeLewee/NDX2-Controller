"""Opt-in bounded metadata reads for the read-only live trial."""
from collections import OrderedDict
import threading
import time

from tidal_library import TidalLibrary


class DeferredRelated:
    """One outstanding provider read; cold/expired links are absent until verified.

    The source must be a dedicated catalogue instance, not shared with foreground
    requests. No audio, account token or artwork object crosses this worker.
    """
    def __init__(self, source, clock=time.monotonic):
        self.source, self.clock = source, clock
        self.lock = threading.Lock()
        self.cache = OrderedDict()
        self.busy = False

    def related(self, reference):
        with self.lock:
            cached = self.cache.get(reference)
            if cached and self.clock() < cached[0]:
                self.cache.move_to_end(reference)
                return [dict(item) for item in cached[1]]
            if not self.busy:
                self.busy = True
                threading.Thread(target=self._load, args=(reference,), daemon=True).start()
            return []

    def _load(self, reference):
        try:
            items = self.source.related(reference)[:32]
            lifetime = 60
        except Exception:
            items, lifetime = [], 10
        with self.lock:
            self.cache[reference] = (self.clock() + lifetime, items)
            self.cache.move_to_end(reference)
            while len(self.cache) > 32:
                self.cache.popitem(last=False)
            self.busy = False


class ObservedReadOnlyLibrary(TidalLibrary):
    """Never scan a collection in response to a player's membership poll.

    A recent page proves positive membership only. Missing/expired observations
    remain unknown, never unsaved. The existing writable POC adapter is unchanged.
    """
    def __init__(self, catalog, clock=time.monotonic, sleep=time.sleep):
        super().__init__(catalog, clock, sleep, read_only=True)
        self.observed = OrderedDict()

    def page(self, kind, cursor=None):
        result = super().page(kind, cursor)
        for item in result['items']:
            self.observed[item['reference']] = self.clock() + 60
            self.observed.move_to_end(item['reference'])
            while len(self.observed) > 256:
                self.observed.popitem(last=False)
        return result

    def contains(self, reference, fresh=False):
        self.parse(reference)
        if self.connected and not fresh and self.clock() < self.observed.get(reference, 0):
            return True
        return None

    def disconnect(self):
        super().disconnect()
        self.observed.clear()

"""Host-side enrollment foundation; no discovery, trust download or hardware writes.

Call only after a local operator supplies independently verified origin/trust and a
single-use code. Status/results never contain credentials. No pairing retry.
"""
import hashlib
from pathlib import Path
import re
import urllib.error
from urllib.parse import urlsplit
from m2_client import Client


class EnrollmentError(RuntimeError):
    pass


def binding(url, trust):
    # Client enforces HTTPS origin and creates a verifying TLS context.
    parsed=urlsplit(url)
    if not parsed.hostname or parsed.query or parsed.fragment: raise EnrollmentError('INVALID_ORIGIN')
    client=Client(url,trust)
    return client, {'origin':client.url,'trust_sha256':hashlib.sha256(Path(trust).read_bytes()).hexdigest()}


def controller_client(vault, url, trust):
    client, target=binding(url,trust)
    record=vault.data.get('controller',{})
    enrollment=vault.data.get('enrollment')
    if enrollment is not None or 'origin' in record or 'trust_sha256' in record:
        if not isinstance(enrollment,dict): raise EnrollmentError('ENROLLMENT_REQUIRED')
        if enrollment.get('version')!=1 or enrollment.get('state')!='paired' or any(record.get(k)!=v for k,v in target.items()):
            raise EnrollmentError('ENROLLMENT_REQUIRED')
        if (not isinstance(record.get('device'),str) or not re.fullmatch('[0-9a-f]{24}',record['device']) or
            not isinstance(record.get('credential'),str) or not re.fullmatch('[A-Za-z0-9_-]{43}',record['credential'])):
            raise EnrollmentError('ENROLLMENT_REQUIRED')
    # Preserve legacy fixture records. New enrollments always carry a binding.
    if not isinstance(record.get('credential'),str) or not record['credential']:
        raise EnrollmentError('ENROLLMENT_REQUIRED')
    client.credential=record['credential']
    return client


class Enrollment:
    def __init__(self, vault, url=None, trust=None):
        self.vault,self.url,self.trust=vault,url,trust
        self.storage_uncertain=False
        self.target=binding(url,trust)[1] if url is not None and trust is not None else None

    def status(self):
        with self.vault.lock:
            record=self.vault.data.get('enrollment')
            if record is None:
                controller=self.vault.data.get('controller',{})
                state='recovery_required' if 'origin' in controller or 'trust_sha256' in controller else 'legacy' if controller else 'unpaired'
            elif (not isinstance(record,dict) or record.get('version')!=1 or
                  record.get('state') not in ('pending','paired','authorization_required')):
                state='recovery_required'
            else: state=record['state']
            if self.storage_uncertain: state='storage_uncertain'
            elif state=='pending': state='outcome_unknown'
            result={'state':state}
            device=self.vault.data.get('controller',{}).get('device')
            if isinstance(device,str) and re.fullmatch('[0-9a-f]{24}',device): result['device']=device
            return result

    def _save(self, change):
        try: self.vault.update(change)
        except Exception:
            self.storage_uncertain=True
            raise EnrollmentError('STORAGE_UNCERTAIN') from None

    def pair(self, code):
        with self.vault.lock:
            if self.status()['state']!='unpaired': raise EnrollmentError('LOCAL_RECOVERY_REQUIRED')
            if not isinstance(code,str) or not re.fullmatch('[A-Za-z0-9_-]{32}',code):
                raise EnrollmentError('INVALID_SETUP_CODE')
            if self.target is None: raise EnrollmentError('INVALID_ORIGIN')
            client,target=binding(self.url,self.trust)
            if target!=self.target: raise EnrollmentError('TRUST_CHANGED')
            # This durable intent precedes the one and only remote pairing request.
            self._save(lambda d:d.update(enrollment={'version':1,'state':'pending',**target}))
            try:
                result=client.post('/v1/pair',{'code':code})
                if (not isinstance(result,dict) or set(result)!={'device','credential'} or
                    not isinstance(result['device'],str) or not re.fullmatch('[0-9a-f]{24}',result['device']) or
                    not isinstance(result['credential'],str) or not re.fullmatch('[A-Za-z0-9_-]{43}',result['credential'])):
                    raise ValueError()
            except Exception:
                raise EnrollmentError('PAIRING_OUTCOME_UNKNOWN') from None
            self._save(lambda d:d.update(controller={**result,**target},enrollment={'version':1,'state':'paired'}))
            return self.status()

    def verify(self):
        with self.vault.lock:
            if self.storage_uncertain: raise EnrollmentError('STORAGE_UNCERTAIN')
            try:
                client=controller_client(self.vault,self.url,self.trust)
                response=client.request('snapshot')
                if response.get('outcome')!='observed': raise ValueError()
            except urllib.error.HTTPError as exc:
                if exc.code==401:
                    self._save(lambda d:d.update(enrollment={'version':1,'state':'authorization_required'}))
                    raise EnrollmentError('AUTHORIZATION_REQUIRED') from None
                raise EnrollmentError('BRIDGE_UNAVAILABLE') from None
            except EnrollmentError: raise
            except Exception: raise EnrollmentError('BRIDGE_UNAVAILABLE') from None
            return {'state':'connected','device':self.status().get('device'),'fixture':response.get('fixture') is True}

    def forget(self):
        # Explicit local action only. It cannot revoke an issued bridge credential.
        with self.vault.lock:
            if self.storage_uncertain: raise EnrollmentError('STORAGE_UNCERTAIN')
            def change(data):
                data.pop('controller',None); data.pop('enrollment',None)
            self._save(change)
            return self.status()

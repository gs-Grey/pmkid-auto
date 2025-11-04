import multiprocessing as mp
import time
import json
import os
import signal

import pmkidauto.file_man as fm
from pmkidauto.check import Check


class CrackOnly:
    def __init__(self, wordlist_name: str, hash_file='hashes.22000', pot_file='found.potfile', single_thread=False, verbose=False):
        self.hash_file_name = hash_file
        self.hash_file = fm.try_open_read_file(self.hash_file_name)
        self.pot_file = pot_file
        self._wordlist_name = os.path.abspath(wordlist_name)
        self.single_thread = single_thread
        self.verbose = verbose
        self.verbose_interval = 100
        
        self.session_file = '.pmkidauto_session'
        self.resume_line = 0
        self.last_checked_line = 0
        self.processes = []
        
        self.load_session()

    def load_session(self):
        if not os.path.exists(self.session_file):
            return
        try:
            with open(self.session_file, 'r') as f:
                data = json.load(f)
            if data.get('hash_file') == self.hash_file_name and data.get('wordlist') == self._wordlist_name:
                self.resume_line = int(data.get('last_line', 0))
                if self.resume_line > 0:
                    print(f'[INFO] Resuming session for wordlist "{os.path.basename(self._wordlist_name)}" from line {self.resume_line}.')
        except (json.JSONDecodeError, FileNotFoundError):
            self.resume_line = 0

    def save_session(self):
        session_data = {
            'hash_file': self.hash_file_name,
            'wordlist': self._wordlist_name,
            'last_line': self.last_checked_line
        }
        with open(self.session_file, 'w') as f:
            json.dump(session_data, f)
        print(f'[INFO] Progress saved. Last checked line: {self.last_checked_line}.')

    def clear_session(self):
        if os.path.exists(self.session_file):
            os.remove(self.session_file)

    def handle_interrupt(self):
        if self.single_thread:
            self.save_session()
        else:
            # For multiprocessing, terminate children before saving
            for p in self.processes:
                p.terminate()
                p.join()
            print("[INFO] Worker processes terminated.")
            # Session saving in multiproc is complex; for now, we just exit cleanly
            # A more advanced implementation would require inter-process communication

    def bo_force(self, hash_line):
        # In multiprocessing, child processes ignore Ctrl+C
        if not self.single_thread:
            signal.signal(signal.SIGINT, signal.SIG_IGN)

        wd = fm.try_open_read_file(self._wordlist_name)
        if not wd:
            return

        ck = Check(hash_line)
        essid = ck.essid.decode(errors='ignore')
        if fm.search_in_potfile(self.pot_file, hash_line, essid):
            return

        if self.single_thread:
            print(f'[!] Cracking hash for AP "{essid}"...')
        
        start_time = time.time()
        
        # Skip lines if resuming
        for _ in range(self.resume_line):
            next(wd)
        
        self.last_checked_line = self.resume_line

        for i, line in enumerate(wd, start=self.resume_line + 1):
            self.last_checked_line = i
            word = line.strip()

            if self.verbose and i % self.verbose_interval == 0:
                elapsed_time = time.time() - start_time
                speed = (i - self.resume_line) / elapsed_time if elapsed_time > 0 else 0
                print(f'    [INFO] Progress: line {i} checked ({speed:.1f} p/s). Trying: "{word}"', end='\r')

            if len(word) <= 7:
                continue

            if ck.check_pass(word):
                print(f'\n    [FOUND!] => ESSID:"{essid}": PSK:"{word}"')
                to_potfile = f'{hash_line}:{word}'
                print(f'    [HASH] => {to_potfile}')
                fm.create_write_file(self.pot_file, to_potfile, 'a+')
                self.clear_session()
                return
        
        print(' ' * 80, end='\r')
        print(f'[!] AP "{essid}" wordlist exhausted. Total passwords checked: {self.last_checked_line}')
        self.clear_session()

    def start(self):
        if self.single_thread:
            print('[!] Running in single-thread mode...')
        else:
            print('[!] Running in multiprocessing mode...')
            
        if not self.hash_file:
            print(f"[!] Hash file '{self.hash_file_name}' not found or is empty.")
            return

        for hash_line in self.hash_file:
            if all([hash_line, not hash_line == '\n']):
                hl = hash_line.rstrip()
                if self.single_thread:
                    self.bo_force(hl)
                else:
                    p = mp.Process(target=self.bo_force, args=(hl,))
                    self.processes.append(p)
                    p.start()
        
        # Wait for all processes to finish
        for p in self.processes:
            p.join()

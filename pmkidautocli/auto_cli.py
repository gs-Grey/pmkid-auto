import argparse
import sys

from pmkidauto import auto
from pmkidauto import crack_only
from pmkidauto import file_man as fm

_SCAN_TIME = '7'
_TIME_OUT = '15'


def main():
    # We create the instance outside the try block to have access to it in `except`
    cracker = None
    try:
        parser = argparse.ArgumentParser()
        parser.add_argument('-i', '--interface',
                            help='wlan interface')
        parser.add_argument('-w', '--wordlist',
                            help='wordlist file')
        parser.add_argument('-s', '--scan_time',
                            help=f'AP scaning time (default {_SCAN_TIME} seconds)',
                            default=_SCAN_TIME)
        parser.add_argument('-t', '--time_out',
                            help=f'timeout to retrieve PMKID (default {_TIME_OUT} seconds)',
                            default=_TIME_OUT)
        parser.add_argument('-c', '--crack_only',
                            help='crack_only-mode on hashes.22000 file',
                            action='store_true')
        parser.add_argument('-st', '--single',
                            dest='single_thread',
                            help='run cracking in a single thread (slower but more stable)',
                            action='store_true')
        parser.add_argument('-v', '--verbose',
                            help='show cracking progress and current password being tested',
                            action='store_true')

        arg = parser.parse_args()

        if arg.crack_only:
            print('[!] Crack_only-mode')
            if arg.wordlist:
                fm.try_open_read_file(arg.wordlist)
                cracker = crack_only.CrackOnly(
                    arg.wordlist,
                    single_thread=arg.single_thread,
                    verbose=arg.verbose
                )
                cracker.start()
            else:
                print('[!] You must specify a wordlist to --wordlist argument')
        else:
            if arg.interface:
                if arg.wordlist:
                    fm.try_open_read_file(arg.wordlist)
                else:
                    print('[!] Capture-only mode, to brute-force specify the --wordlist argument')
                auto.Auto(arg.interface, arg.wordlist, arg.scan_time, arg.time_out).start()
            else:
                print('[!] No interface (-i) or crack-only (-c) selected, type -h for help.')

    except KeyboardInterrupt:
        print("\n[!] Process interrupted by user.")
        if cracker:
             # This will save session on Ctrl+C
             cracker.handle_interrupt()
        print("[!] Exiting gracefully...")
        sys.exit(0)

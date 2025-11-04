# pmkid-auto

Automates the capture and crack of PMKID hashes, based on wpa_supplicant manager.

**Without using monitor mode**, runs on any Debian-based distro or architecture like laptops with internal wifi, rooted smartphones (using Termux / NetHunter) or raspberry pi.
And of course with a usb dongle.


This program uses the debug mode from wpa_suplicant to retrieve pmkid from each parsed AP, and simultaneously uses an internal (very slow) cracker to retrieve the PSK password.

The program creates 3 files:

**hashes.22000** Pmkids found in Hashcat 22000 mode

**found.potfile** Cracked hashs (hashcat style)

**wpa_supp.conf** wpa_supplicant Configuration file

## requirements

    pkg update && pkg upgrade && pkg install root-repo && pkg install python git wpa-supplicant

- wpa_supplicant (```pkg install wpa-supplicant```)
- python >=3.6 (```pkg install python git```)

## instalation


    pip install --upgrade pip setuptools wheel pbkdf2 && pip install --no-build-isolation git+https://github.com/gs-Grey/pmkid-auto.git
or

    sudo pip3 install git+git://github.com/gs-Grey/pmkid-auto.git


or

    sudo pip3 install --upgrade https://github.com/gs-Grey/pmkid-auto/tarball/master
    

## usage

**Default Mode:**

Once installed, simply call **pmkidauto** from the command line as superuser:

    sudo pmkidauto -i wlan0 -s 10 -t 15

or

    sudo pmkidauto -i wlan0 -w tiny_wordlist.txt

Use the optional **-s** flags to set the APs **--scan_time** and **-t** for the PMKID hash recovery **--time_out**.
The defaults are scan_time=7  and time_out=15

    sudo pmkidauto -i wlan0 -w tiny_wordlist.txt -s 10 -t 20
    
   
**Crack only mode:**

Use the **-c** flag to only crack the hashes, in the hashes.22000 file.

    
    sudo pmkidauto -c -w tiny_wordlist.txt -v
    

You can also importing pmkidauto as module and using the Classes Auto and CrackOnly.

    from pmkidauto import Auto, CrackOnly

    auto = Auto('wlx8416f911a4b1',
                wordlist='tiny_wordlist.txt',
                scan_time='5',
                time_out='20')
    auto.start()

    crack_only = CrackOnly('tiny_wordlist.txt',
                           hash_file='my_pmkid_hashes.22000',
                           pot_file='my_potfile.txt')
    crack_only.start()
    
**help:**

    -i, --interface   INTERFACE   wlan interface
    -w, --wordlist    WORDLIST    wordlist file
    -s, --scan_time   SCAN_TIME   AP scaning time (default 7 seconds)
    -t, --time_out    TIME_OUT    timeout to retrieve PMKID (default 15 seconds)
    -c,--crack_only               crack_only-mode on hashes.22000 file
    -v,--verbose                  Use the -v flag to enable verbose output for the crack_only-mode


## You might need some of this:

**Fix .suroot mkdir permission denied:**

    rm -rf /data/data/com.termux/files/home/.suroot && pkg reinstall tsu
    
**Try autoinstall:**

    apt update && apt upgrade && apt install hashcat hcxtools hcxdumptool

**Try to install hcxtools manually:**

    git clone https://github.com/ZerBea/hcxtools.git
    cd hcxtools
    make -j $(nproc)
    make install
    
**Try to install hcxdumptool manually:**

    git clone https://github.com/ZerBea/hcxdumptool.git
    cd hcxdumptool
    make -j $(nproc)
    make install

**Try to install Hashcat somehow:**

    pkg install tur-repo
    pkg install git clang make opencl-headers gnupg curl pocl

    curl -fLO https://github.com/Auxilus/Auxilus-repo/raw/main/auxilus-repo.deb


    wget https://hashcat.net/files/hashcat-7.1.2.tar.gz
    tar -xvf hashcat-7.1.2.tar.gz
    cd hashcat-7.1.2
    make
    make install
    hashcat --version
    hashcat -b


The PMKID hash was discovered by the creator of Hashcat @jsteube, described here: https://hashcat.net/forum/thread-7717.html


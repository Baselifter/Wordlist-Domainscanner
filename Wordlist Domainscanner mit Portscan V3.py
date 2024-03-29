#
# __________  _____________________   
# \______   \/  |  \______  \      \  
#  |     ___/   |  |_  /    /   |   \ 
#  |    |  /    ^   / /    /    |    \
#  |____|  \____   | /____/\____|__  /
#               |__|               \/ 
#======================================================================
#	Code by:	Baselifter		Date:	29.03.2024
#	Version: 	0.1			    Mail:	project.northstorm@gmail.com
#----------------------------------------------------------------------
#	License: DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
#                    Version 2, December 2004
#
# 				  Copyright (C) 2004 Sam Hocevar
#  			  14 rue de Plaisance, 75014 Paris, France
# Everyone is permitted to copy and distribute verbatim or modified
# copies of this license document, and changing it is allowed as long
# 					  as the name is changed.
#
#            DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
#   TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION
#
#  				0. You just DO WHAT THE FUCK YOU WANT TO.
#---------------------------------------------------------------------- 



import requests
import csv
from datetime import datetime
import os
import re
import socket
from concurrent.futures import ThreadPoolExecutor


def read_wordlist(domain_extension):
    desktop_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
    wordlist_file = os.path.join(desktop_path, 'Wordlist.txt')
    with open(wordlist_file, mode='r', encoding='utf-8') as file:
        wordlist = file.readlines()
    # Umlaute ersetzen
    umlaute_mapping = {'ä': 'ae', 'ö': 'oe', 'ü': 'ue', 'ß': 'ss'}
    replaced_wordlist = []
    for word in wordlist:
        for umlaut, replacement in umlaute_mapping.items():
            word = word.replace(umlaut, replacement)
        word = re.sub(r'[^a-zA-Z0-9]', '', word.strip())  # Sonderzeichen entfernen
        replaced_wordlist.append(word + f".{domain_extension}")
    return replaced_wordlist


def scan_ports(domain, ports):
    open_ports = []
    for port in ports:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.5)  # Timeout-Wert reduzieren
                result = s.connect_ex((domain, port))
                if result == 0:
                    open_ports.append(port)
        except Exception as e:
            pass  # Fehler ignorieren
    return open_ports


def get_ip_address(domain):
    try:
        return socket.gethostbyname(domain)
    except Exception as e:
        return 'N/A'


def scan_domain(domain):
    url = f"http://{domain}"  # You can also use https:// if needed
    try:
        response = requests.get(url, allow_redirects=False, timeout=1)  # Timeout-Wert reduzieren
        if response.status_code == 200:
            server_time = response.headers.get('Date', 'N/A')
            ip_address = get_ip_address(domain)
            metadata = response.headers.get('Server', 'N/A')  # Example header, adjust as needed
            open_ports = scan_ports(domain, PORTS_TO_SCAN)
            result = (datetime.now(), domain, "Success", ip_address, server_time, metadata, open_ports)
            write_to_csv([result])
            print(f"Scanned domain: {domain} - Status: Success")
    except requests.ConnectionError:
        print(f"Scanned domain: {domain} - Status: Connection Error")
    except requests.Timeout:
        print(f"Scanned domain: {domain} - Status: Timeout")
    except Exception as e:
        print(f"Scanned domain: {domain} - Status: Error")


def write_to_csv(results):
    desktop_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
    csv_file = os.path.join(desktop_path, 'Scan Ergebnisse.csv')
    with open(csv_file, mode='a', newline='', encoding='utf-8') as file:  # 'a' zum Anhängen an die Datei
        writer = csv.writer(file)
        for result in results:
            writer.writerow(result)


def main():
    domain_extension = input("Bitte geben Sie die Domainendung (z.B. .de, .ch, .com) ein: ")

    wordlist = read_wordlist(domain_extension)

    # Parallelisierte Ausführung der Scan-Vorgänge
    with ThreadPoolExecutor(max_workers=30) as executor:
        executor.map(scan_domain, wordlist)

    print("Der Scanvorgang wurde abgeschlossen.")
    print("Die Scan-Ergebnisse wurden erfolgreich in 'Scan Ergebnisse.csv' auf dem Desktop gespeichert.")


if __name__ == "__main__":
    PORTS_TO_SCAN = [7, 11, 13, 18, 20, 21, 22, 23, 25, 42, 43, 53, 69, 70, 79, 80, 88, 105, 107, 109, 110, 113, 115, 117, 119, 123, 137, 138, 139, 143, 161, 162, 194, 209, 220, 443, 444, 445, 512,
                     513, 514, 515, 517, 518, 520, 521, 531, 532, 533, 546, 547, 556, 631, 873, 992, 993, 995, 1433, 1434, 2008, 2010, 2049, 3306, 4321, 11371, 25565, 26000, 27027, 33434]
    main()
import socket
import threading
import json
import logging
import subprocess
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

HOST = '0.0.0.0'
PORT = 5000
CONFIG_FILE = 'config.json'

def load_config():
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Failed to load config: {e}")
        return {}

CONFIG = load_config()

def proceseaza_client(conexiune, adresa):
    logging.info(f"S-a conectat un client nou de la: {adresa}")
    try:
        # Citim ce trimite clientul, linie cu linie
        f = conexiune.makefile('r', encoding='utf-8')
        while True:
            linie = f.readline()
            if not linie:
                break # Clientul a inchis conexiunea
            
            try:
                cerere = json.loads(linie)
            except json.JSONDecodeError:
                trimite_raspuns(conexiune, {"status": "eroare", "message": "JSON invalid, te rog verifica formatul"})
                continue
            
            actiune = cerere.get("action")
            
            if actiune == "list_apps":
                aplicatii_disp = {}
                if "apps" in CONFIG:
                    for nume_app, operatii in CONFIG["apps"].items():
                        aplicatii_disp[nume_app] = list(operatii.keys())
                trimite_raspuns(conexiune, {"status": "success", "data": aplicatii_disp})
                
            elif actiune == "execute":
                app = cerere.get("app")
                operatie = cerere.get("operation")
                
                if "apps" not in CONFIG or app not in CONFIG["apps"]:
                    trimite_raspuns(conexiune, {"status": "eroare", "message": f"Nu am gasit aplicatia '{app}' in config."})
                    continue
                    
                if operatie not in CONFIG["apps"][app]:
                    trimite_raspuns(conexiune, {"status": "eroare", "message": f"Operatia '{operatie}' nu e permisa pe '{app}'."})
                    continue
                
                comanda_de_rulat = CONFIG["apps"][app][operatie]
                logging.info(f"Execut comanda pentru {app} -> {operatie}: {comanda_de_rulat}")
                
                try:
                    # Rulam comanda efectiv in sistemul de operare
                    rezultat = subprocess.run(comanda_de_rulat, shell=True, capture_output=True, text=True, timeout=10)
                    trimite_raspuns(conexiune, {
                        "status": "success",
                        "exit_code": rezultat.returncode,
                        "output": rezultat.stdout,
                        "error": rezultat.stderr
                    })
                except subprocess.TimeoutExpired:
                    trimite_raspuns(conexiune, {"status": "eroare", "message": "Comanda a durat prea mult si a luat timeout."})
                except Exception as e:
                    trimite_raspuns(conexiune, {"status": "eroare", "message": f"A picat executia comenzii: {str(e)}"})
                    
            else:
                trimite_raspuns(conexiune, {"status": "eroare", "message": "Actiune necunoscuta"})
                
    except ConnectionResetError:
        logging.info(f"Clientul {adresa} a dat disconnect (Connection reset)")
    except Exception as e:
        logging.error(f"Eroare generala pe clientul {adresa}: {e}")
    finally:
        conexiune.close()
        logging.info(f"Am inchis conexiunea cu {adresa}")

def trimite_raspuns(conexiune, dictionar_raspuns):
    try:
        date_trimise = json.dumps(dictionar_raspuns) + "\n"
        conexiune.sendall(date_trimise.encode('utf-8'))
    except Exception as e:
        logging.error(f"Eroare la trimiterea raspunsului inapoi: {e}")

def start_server():
    if not CONFIG:
        logging.error("Nu am gasit fisierul de config sau e gol, ma opresc.")
        return
        
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Punem asta ca sa nu ne mai dea adresa blocata cand dam restart
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        server.bind((HOST, PORT))
        server.listen()
        logging.info(f"Serverul a pornit. Asteptam conexiuni pe {HOST}:{PORT}")
    except Exception as e:
        logging.error(f"Eroare la pornire pe port: {e}")
        return

    try:
        while True:
            conexiune_noua, adresa_client = server.accept()
            # Facem un thread separat ca sa mearga mai multi clienti deodata
            fir = threading.Thread(target=proceseaza_client, args=(conexiune_noua, adresa_client))
            fir.daemon = True 
            fir.start()
    except KeyboardInterrupt:
        logging.info("Am apasat Ctrl+C, opresc serverul.")
    finally:
        server.close()

if __name__ == "__main__":
    start_server()

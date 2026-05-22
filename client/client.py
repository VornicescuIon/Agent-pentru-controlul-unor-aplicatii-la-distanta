import socket
import json
import sys

HOST = '127.0.0.1'
PORT = 5000

def trimite_cerere(socket_client, cerere_dict):
    try:
        # transformam dictionarul in string json si punem \n la final
        date = json.dumps(cerere_dict) + "\n"
        socket_client.sendall(date.encode('utf-8'))
        
        # citim raspunsul de la server
        f = socket_client.makefile('r', encoding='utf-8')
        linie = f.readline()
        if not linie:
            return None
        return json.loads(linie)
    except Exception as e:
        print(f"Eroare la comunicarea cu serverul: {e}")
        return None

def main():
    socket_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        socket_client.connect((HOST, PORT))
        print(f"Ne-am conectat la serverul {HOST}:{PORT}\n")
    except Exception as e:
        print(f"Eroare: nu ne-am putut conecta la server: {e}")
        sys.exit(1)

    try:
        while True:
            print("=== MENIU PROIECT ===")
            print("1. Afiseaza lista de aplicatii")
            print("2. Trimite comanda (executa)")
            print("3. Iesire")
            optiune = input("Alege o varianta: ").strip()

            if optiune == "1":
                raspuns = trimite_cerere(socket_client, {"action": "list_apps"})
                if raspuns and raspuns.get("status") == "success":
                    print("\nAplicatii gasite in configurare:")
                    for aplicatie, operatii in raspuns.get("data", {}).items():
                        print(f" - {aplicatie}: {', '.join(operatii)}")
                    print()
                else:
                    print(f"\nEroare de la server: {raspuns}\n")

            elif optiune == "2":
                nume_app = input("Numele aplicatiei (ex: web_server): ").strip()
                nume_op = input("Operatia (ex: start, stop): ").strip()
                
                print(f"\nTrimitem cererea pentru {nume_op} pe {nume_app}...")
                raspuns = trimite_cerere(socket_client, {"action": "execute", "app": nume_app, "operation": nume_op})
                
                if raspuns:
                    if raspuns.get("status") == "success":
                        print(f"Comanda s-a executat cu SUCCES!")
                        print(f"Cod de iesire (Exit Code): {raspuns.get('exit_code')}")
                        if raspuns.get('output'):
                            print(f"Rezultat comanda:\n{raspuns.get('output').strip()}")
                        if raspuns.get('error'):
                            print(f"Erori comanda:\n{raspuns.get('error').strip()}")
                    else:
                        print(f"Eroare de executie: {raspuns.get('message')}")
                print()
                
            elif optiune == "3":
                print("Inchidem clientul. Pa!")
                break
            else:
                print("Nu stiu optiunea asta, incearca 1, 2 sau 3.\n")
                
    except KeyboardInterrupt:
        print("\nAm apasat Ctrl+C, inchidem.")
    finally:
        socket_client.close()

if __name__ == "__main__":
    main()

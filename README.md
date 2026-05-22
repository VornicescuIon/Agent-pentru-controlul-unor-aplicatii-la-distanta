# Proiect la Rețele de calculatoare: Server de Control de la Distanță (Client-Server)
Nume: Voinescu Ion 
Materia: Rețele de Calculatoare

## Descriere scurtă
Proiectul constă într-o aplicație client-server scrisă în Python, care ne permite să executăm comenzi pe un server de la distanță. Comenzile sunt prestabilite într-un fișier de configurare (pentru a nu permite executarea oricărui cod periculos). Am folosit protocoale TCP și JSON pentru comunicare.

## Arhitectură
- **Server:** Folosește modulele `socket` și `threading` pentru a accepta mai mulți clienți simultan. Fiecare client nou e preluat de un thread separat. Serverul e băgat și într-un container Docker ca să fie mai ușor de pornit.
- **Client:** E un simplu meniu în consolă. Se conectează la server și poți alege din el opțiunile dorite.

## Cum se rulează

1. Porniți serverul (din Docker):
```bash
docker compose up --build
```

2. După ce serverul a pornit, deschideți alt terminal, intrați în folderul proiectului și rulați clientul:
```bash
python client/client.py
```

## Cum se testează
1. Din meniul care apare, apăsați `1` pentru a vedea ce aplicații putem controla (ex: `web_server`, `database`).
2. Apăsați `2` ca să trimitem o comandă. La aplicație băgați `web_server` și la operație `status`.
3. Puteți deschide și un al doilea terminal cu `client.py` ca să testați că serverul acceptă conexiuni concurente (merg amândoi clienții în același timp).

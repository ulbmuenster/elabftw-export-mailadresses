Dieses Script nutzt die elabFTW API um Listen von Emailadressen zu erzeugen. Es können entweder die Adressen aller aktiven User (= User die sich schon einmal eingeloggt haben) oder die aller aktiven Team-Admins exportiert werden. Als Exportformate stehen bereit;: Textdatei (pro Zeile eine Adresse) für den Import in Listserv oder einen Export für MS Outlook, bei dem die Adressen mit ` ; ` separiert sind.

Die Ausgabedateien landen im Ordner `output`.

Man benötigt einen API Key, den man unter https://<elabftw-url>/ucp.php?tab=4 erzeugen kann. Er wird am Anfang abgefragt.

Ausgeführt kann das Script entweder lokal nutzen. Oder eben über `docker compose` - dann muss das aber auch [installiert](https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository) sein. 

## Pip

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python get_mails.py
deactivate
```

## uv

Install `uv` (e.g. `curl -LsSf https://astral.sh/uv/install.sh | sh`) - see https://docs.astral.sh/uv/getting-started/installation/ for all instructions.

```bash
uv run get_mails.py
```

## Docker compose

```bash
docker compose run mailscript
```
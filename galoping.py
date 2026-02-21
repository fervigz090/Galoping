import subprocess
import platform
import time
import os
from datetime import datetime

def clear():
    os.system('cls' if platform.system() == 'Windows' else 'clear')

def ping_once(ip: str) -> bool:
    param = "-n" if platform.system() == "Windows" else "-c"
    cmd = ["ping", param, "1", ip]
    try:
        r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return r.returncode == 0
    except Exception:
        return False

def print_table(ip: str, history: list[dict], live: dict, max_rows: int = 12):
    clear()
    print(f"Ping en tiempo real a {ip}  |  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Cabecera
    print("+---------------------+----------+----------+----------+----------+------------------------------+")
    print("| Timestamp           | Enviados | Recibidos| Perdidos | % Pérd.  | Racha perdida cerrada (>2)  |")
    print("+---------------------+----------+----------+----------+----------+------------------------------+")

    # Historial (últimas N filas)
    for row in history[-max_rows:]:
        print(
            f"| {row['ts']:<19} | {row['sent']:>8} | {row['recv']:>8} | {row['lost']:>8} | "
            f"{row['loss_pct']:>8.2f}% | {str(row['closed_streak']):^28} |"
        )

    # Separador y fila LIVE
    print("+---------------------+----------+----------+----------+----------+------------------------------+")
    live_streak_display = live["current_streak"] if live["current_streak"] > 2 else "-"
    print(
        f"| {'LIVE':<19} | {live['sent']:>8} | {live['recv']:>8} | {live['lost']:>8} | "
        f"{live['loss_pct']:>8.2f}% | {str(live_streak_display):^28} |"
    )
    print("+---------------------+----------+----------+----------+----------+------------------------------+")

def main(ip: str):
    sent = 0
    recv = 0
    consecutive_lost = 0

    history: list[dict] = []

    try:
        while True:
            sent += 1
            ok = ping_once(ip)

            if ok:
                # Si veníamos de una racha >2, la cerramos y la registramos en una fila “congelada”
                if consecutive_lost > 2:
                    lost = sent - recv  # ojo: todavía no sumamos este recv, va después
                    # Como este ping fue OK, primero actualizamos recv para el snapshot “tras recuperación”
                    recv += 1
                    lost = sent - recv
                    loss_pct = (lost / sent) * 100

                    history.append({
                        "ts": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "sent": sent,
                        "recv": recv,
                        "lost": lost,
                        "loss_pct": loss_pct,
                        "closed_streak": consecutive_lost
                    })

                    consecutive_lost = 0  # empezamos nueva fila LIVE a partir de ahora
                else:
                    recv += 1
                    consecutive_lost = 0
            else:
                consecutive_lost += 1

            lost = sent - recv
            loss_pct = (lost / sent) * 100

            live = {
                "sent": sent,
                "recv": recv,
                "lost": lost,
                "loss_pct": loss_pct,
                "current_streak": consecutive_lost
            }

            print_table(ip, history, live, max_rows=12)
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n⛔ Monitor detenido por el usuario")

if __name__ == "__main__":
    ip = input("Introduce la IP a monitorizar: ").strip()
    main(ip)
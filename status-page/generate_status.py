#!/usr/bin/env python3

import socket
import subprocess
import datetime

SERVICES = [
    {"name": "My App", "Port": 8080, "systemd": "myapp"},
   ]

def check_port(port):
    if port is None:
        return None
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        s.connect(("127.0.0.1", port))
        s.close()
        return True
    except:
        return False

def check_systemd(service):
    if service is None:
        return None
    result = subprocess.run(
        ["systemctl", "is-active", service],
        capture_output=True, text=True
    )
    return result.stdout.strip() == "active"

def get_status(svc):
    port_up = check_port(svc["port"])
    systemd_up = check_systemd(svc["systemd"])

    if port_up is False or systemd_up is False:
        return "down"
    if port_up is True or systemd_up is True:
        return "up"
    return "unknown"

def render_html(results):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    all_up = all(r["status"] == "up" for r in results)

    rows = ""
    for r in results:
        badge = {
            "up":      '<span class="badge up">UP</span>',
            "down":    '<span class="badge down">DOWN</span>',
            "unknown": '<span class="badge unknown">UNKNOWN</span>',
        }[r["status"]]

        port_str = str(r["port"]) if r["port"] else "—"
        systemd_str = r["systemd"] if r["systemd"] else "—"

        rows += f"""
        <tr>
            <td>{r['name']}</td>
            <td>{port_str}</td>
            <td>{systemd_str}</td>
            <td>{badge}</td>
        </tr>"""

    overall_class = "all-up" if all_up else "has-down"
    overall_text = "All systems operational" if all_up else "Some services are down"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="refresh" content="60">
    <title>Server Status</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Courier New', monospace; background: #0f0f0f; color: #e0e0e0; padding: 40px 20px; }}
        h1 {{ font-size: 1.4rem; font-weight: normal; margin-bottom: 6px; color: #fff; }}
        .subtitle {{ color: #555; font-size: 0.85rem; margin-bottom: 30px; }}
        .overall {{ display: inline-block; padding: 8px 16px; border-radius: 4px; font-size: 0.85rem; margin-bottom: 30px; }}
        .all-up {{ background: #0d2e1a; color: #4caf7d; border: 1px solid #1a5c35; }}
        .has-down {{ background: #2e0d0d; color: #e05c5c; border: 1px solid #5c1a1a; }}
        table {{ width: 100%; max-width: 700px; border-collapse: collapse; }}
        th {{ text-align: left; padding: 10px 14px; font-size: 0.75rem; color: #555; text-transform: uppercase; letter-spacing: 0.08em; border-bottom: 1px solid #1e1e1e; }}
        td {{ padding: 12px 14px; font-size: 0.875rem; border-bottom: 1px solid #1a1a1a; }}
        tr:hover td {{ background: #161616; }}
        .badge {{ padding: 3px 10px; border-radius: 3px; font-size: 0.75rem; font-weight: bold; }}
        .badge.up {{ background: #0d2e1a; color: #4caf7d; }}
        .badge.down {{ background: #2e0d0d; color: #e05c5c; }}
        .badge.unknown {{ background: #1e1e1e; color: #888; }}
    </style>
</head>
<body>
    <h1>homelab status</h1>
    <p class="subtitle">Last updated: {now}</p>
    <div class="overall {overall_class}">{overall_text}</div>
    <table>
        <thead>
            <tr>
                <th>Service</th>
                <th>Port</th>
                <th>Systemd Unit</th>
                <th>Status</th>
            </tr>
        </thead>
        <tbody>{rows}
        </tbody>
    </table>
</body>
</html>"""

if __name__ == "__main__":
    results = []
    for svc in SERVICES:
        results.append({
            "name":    svc["name"],
            "port":    svc["port"],
            "systemd": svc["systemd"],
            "status":  get_status(svc),
        })

    html = render_html(results)
    with open("/var/www/html/status/index.html", "w") as f:
        f.write(html)

# -*- coding: utf-8 -*-
import uuid
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
import requests
from urllib.parse import quote_plus

try:
    from lib.client import cfscraper, USER_AGENT
except Exception:
    try:
        from client import cfscraper, USER_AGENT
    except Exception:
        cfscraper = None
        USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

logger = logging.getLogger("pluto")


def iso_to_dt(s: Optional[str]) -> Optional[datetime]:
    if not s:
        return None
    s = s.strip()
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except Exception:
        for f in ("%Y-%m-%dT%H:%M:%S.%f%z", "%Y-%m-%dT%H:%M:%S%z"):
            try:
                return datetime.strptime(s, f).replace(tzinfo=timezone.utc)
            except Exception:
                continue
    return None


def get_current_time() -> datetime:
    try:
        r = requests.get("http://worldtimeapi.org/api/timezone/America/Sao_Paulo", timeout=6)
        r.raise_for_status()
        dt = iso_to_dt(r.json().get("datetime"))
        return dt.astimezone(timezone.utc) if dt else datetime.now(timezone.utc)
    except Exception:
        return datetime.now(timezone.utc)


def fetch_json(url: str) -> Any:
    headers = {"User-Agent": USER_AGENT}
    if cfscraper:
        resp = cfscraper.get(url, headers=headers, timeout=15)
    else:
        resp = requests.get(url, headers=headers, timeout=15)
    resp.raise_for_status()
    return resp.json()


def playlist_pluto(use_local_file: Optional[str] = None) -> List[Dict[str, Any]]:
    now_utc = get_current_time()
    start = now_utc.strftime("%Y-%m-%dT%H:%M:%SZ")
    stop = (now_utc + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    device_id = str(uuid.uuid4())

    if use_local_file:
        with open(use_local_file, "r", encoding="utf-8") as f:
            channels = json.load(f)
    else:
        url = f"https://api.pluto.tv/v2/channels?start={quote_plus(start)}&stop={quote_plus(stop)}"
        channels = fetch_json(url)

    result: List[Dict[str, Any]] = []

    for ch in channels:
        chan_id = ch.get("id") or ch.get("_id") or ch.get("channelId")
        title = ch.get("name") or ""
        thumb = (ch.get("images", {}).get("logo", {}).get("url") or
                 ch.get("logo", {}).get("path") or
                 ch.get("image_url") or "")

        stream_url = None
        stitched = ch.get("stitched", {}).get("urls", [])
        if stitched:
            url = stitched[0].get("url", "")
            if url:
                stream_url = (
                    url.replace("&deviceMake=", "&deviceMake=Firefox")
                       .replace("&deviceType=", "&deviceType=web")
                       .replace("&deviceId=unknown", f"&deviceId={device_id}")
                       .replace("&deviceModel=", "&deviceModel=web")
                       .replace("&deviceVersion=unknown", "&deviceVersion=82.0")
                       .replace("&appName=&", "&appName=web&")
                       .replace("&appVersion=&", "&appVersion=5.9.1-e0b37ef76504d23c6bdc8157813d13333dfa33a3")
                       .replace("&sid=", f"&sid={device_id}&sessionID={device_id}")
                       .replace("&deviceDNT=0", "&deviceDNT=false")
                    + f"&serverSideAds=false&terminate=false&clientDeviceType=0&clientModelNumber=na&clientID={device_id}"
                    + "|User-Agent=" + quote_plus(USER_AGENT)
                )

        programs = []
        for t in ch.get("timelines", []):
            start_dt = iso_to_dt(t.get("start"))
            stop_dt = iso_to_dt(t.get("stop"))
            ep = t.get("episode", {}) or {}
            programs.append({
                "title": ep.get("name") or t.get("title") or "",
                "description": ep.get("description") or "",
                "start": start_dt,
                "stop": stop_dt,
            })

        programs = sorted([p for p in programs if p["start"]], key=lambda x: x["start"])

        current = next((p for p in programs if p["start"] <= now_utc <= p["stop"]), None)
        next_prog = None
        if current:
            idx = programs.index(current)
            next_prog = programs[idx + 1] if idx + 1 < len(programs) else None

        result.append({
            "id": chan_id,
            "title": title,
            "thumbnail": thumb,
            "stream_url": stream_url,
            "programs": [
                {
                    "title": p["title"],
                    "description": p["description"],
                    "start": p["start"].strftime("%Y-%m-%dT%H:%M:%SZ") if p["start"] else None,
                    "stop": p["stop"].strftime("%Y-%m-%dT%H:%M:%SZ") if p["stop"] else None,
                }
                for p in programs
            ],
            "current_program": current and {
                "title": current["title"],
                "description": current["description"],
                "start": current["start"].strftime("%Y-%m-%dT%H:%M:%SZ"),
                "stop": current["stop"].strftime("%Y-%m-%dT%H:%M:%SZ"),
            },
            "next_program": next_prog and {
                "title": next_prog["title"],
                "description": next_prog["description"],
                "start": next_prog["start"].strftime("%Y-%m-%dT%H:%M:%SZ"),
                "stop": next_prog["stop"].strftime("%Y-%m-%dT%H:%M:%SZ"),
            },
        })

    return result


if __name__ == "__main__":
    data = playlist_pluto()
    print(f"{len(data)} canais carregados")

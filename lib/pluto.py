# -*- coding: utf-8 -*-
"""
Pluto TV helper corrigido.
- Retorna canais com guia de programação (Agora / Próximo).
- Datetimes timezone-aware em UTC.
- Estrutura de retorno compatível: cada canal traz `programs`, `current_program`, `next_program`.
"""

import uuid
import json
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
        USER_AGENT = "pluto-addon/1.0"

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
        fmts = [
            "%Y-%m-%dT%H:%M:%S.%f%z",
            "%Y-%m-%dT%H:%M:%S%z",
            "%Y-%m-%dT%H:%M:%S.%f",
            "%Y-%m-%dT%H:%M:%S",
        ]
        for f in fmts:
            try:
                dt = datetime.strptime(s, f)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt
            except Exception:
                continue
    return None


def get_current_time() -> datetime:
    try:
        r = requests.get("http://worldtimeapi.org/api/timezone/America/Sao_Paulo", timeout=6)
        r.raise_for_status()
        data = r.json()
        dt_str = data.get("datetime") or data.get("utc_datetime")
        dt = iso_to_dt(dt_str)
        if dt is None:
            raise ValueError("invalid time")
        return dt.astimezone(timezone.utc)
    except Exception:
        return datetime.now(timezone.utc)


def fetch_json(url: str, timeout: int = 15) -> Any:
    headers = {"User-Agent": USER_AGENT}
    if cfscraper:
        resp = cfscraper.get(url, headers=headers, timeout=timeout)
    else:
        resp = requests.get(url, headers=headers, timeout=timeout)
    resp.raise_for_status()
    return resp.json()


def format_utc_z(dt: Optional[datetime]) -> Optional[str]:
    if not dt:
        return None
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def playlist_pluto(use_local_file: Optional[str] = None) -> List[Dict[str, Any]]:
    now_utc = get_current_time()
    from_dt = now_utc
    to_dt = from_dt + timedelta(days=1)
    from_str = format_utc_z(from_dt)
    to_str = format_utc_z(to_dt)

    if use_local_file:
        with open(use_local_file, "r", encoding="utf-8") as fh:
            channels = json.load(fh)
    else:
        url = f"https://api.pluto.tv/v2/channels?start={quote_plus(from_str)}&stop={quote_plus(to_str)}"
        channels = fetch_json(url)

    out: List[Dict[str, Any]] = []
    if not isinstance(channels, list):
        return out

    for ch in channels:
        chan_id = ch.get("id") or ch.get("_id") or ch.get("channelId")
        title = ch.get("name") or ch.get("title") or ""
        desc = ch.get("short_description") or ch.get("description") or ""
        thumb = None
        try:
            thumb = ch.get("images", {}).get("logo", {}).get("url") or ch.get("image_url")
        except Exception:
            thumb = ch.get("image_url")

        stream_url = None
        streams = ch.get("streams") or []
        if isinstance(streams, list):
            for s in streams:
                url_s = s.get("url") or s.get("hls_url")
                if url_s:
                    stream_url = url_s
                    break
        if not stream_url:
            stream_url = ch.get("stream") or ch.get("stream_url")

        timelines = ch.get("timelines") or ch.get("timeline") or []
        programs: List[Dict[str, Any]] = []
        for t in timelines:
            start_dt = iso_to_dt(t.get("start"))
            stop_dt = iso_to_dt(t.get("stop"))
            ep = t.get("episode") or {}
            title_p = ep.get("name") or t.get("title") or ""
            desc_p = ep.get("description") or t.get("description") or ""
            programs.append(
                {
                    "title": title_p,
                    "description": desc_p,
                    "start": format_utc_z(start_dt),
                    "stop": format_utc_z(stop_dt),
                    "start_dt": start_dt,
                    "stop_dt": stop_dt,
                }
            )

        programs = sorted(
            [p for p in programs if p.get("start_dt")], key=lambda x: x["start_dt"]
        )

        current_program = None
        next_program = None
        for idx, p in enumerate(programs):
            sd, ed = p.get("start_dt"), p.get("stop_dt")
            if sd and ed and sd <= now_utc <= ed:
                current_program = p
                if idx + 1 < len(programs):
                    next_program = programs[idx + 1]
                break

        if not current_program:
            for p in programs:
                sd = p.get("start_dt")
                if sd and sd > now_utc:
                    next_program = p
                    break

        ordered = []
        if current_program:
            ordered.append(current_program)
            if next_program:
                ordered.append(next_program)
        elif next_program:
            ordered.append(next_program)
        for p in programs:
            if p not in ordered:
                ordered.append(p)
        for p in ordered:
            p.pop("start_dt", None)
            p.pop("stop_dt", None)

        out.append(
            {
                "id": chan_id,
                "title": title,
                "description": desc,
                "thumbnail": thumb,
                "stream_url": stream_url,
                "programs": ordered,
                "current_program": current_program
                and {
                    "title": current_program.get("title"),
                    "description": current_program.get("description"),
                    "start": current_program.get("start"),
                    "stop": current_program.get("stop"),
                },
                "next_program": next_program
                and {
                    "title": next_program.get("title"),
                    "description": next_program.get("description"),
                    "start": next_program.get("start"),
                    "stop": next_program.get("stop"),
                },
                "raw": ch,
            }
        )

    return out


if __name__ == "__main__":
    data = playlist_pluto()
    print(f"Loaded {len(data)} channels")
    if data:
        import pprint

        pprint.pprint(data[0])

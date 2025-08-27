import json
from pathlib import Path
import pandas as pd


# -------- SkillCorner OpenData --------
def _to_seconds(time_val, frame_val=None, fps=None):
    """Parse time as seconds. Accepts numeric, 'MM:SS', 'HH:MM:SS.xxx'. Fallback to frame/fps."""
    if time_val is None or (isinstance(time_val, float) and pd.isna(time_val)):
        pass
    else:
        # numeric string or float/int
        try:
            return float(time_val)
        except Exception:
            # try timedelta parse like '00:01:23.45'
            try:
                return pd.to_timedelta(str(time_val)).total_seconds()
            except Exception:
                pass
    if frame_val is not None and fps:
        try:
            return float(frame_val) / float(fps)
        except Exception:
            return None
    return None


def skillcorner_game(path):
    """
    Load SkillCorner OpenData.
    Returns:
        df columns: [timestamp, period, frame, entity_id, team_id, x, y, speed]
        meta: dict
    """
    p = Path(path)
    sd_path = p / "structured_data.json" if p.is_dir() else p
    md_path = sd_path.with_name("match_data.json")

    with open(sd_path, "r", encoding="utf-8") as f:
        root = json.load(f)

    # frames can be list or dict-with-key
    if isinstance(root, list):
        frames = root
        root_meta = {}
    elif isinstance(root, dict):
        frames = (
            root.get("frames")
            or root.get("data")
            or root.get("positions")
            or root.get("samples")
            or []
        )
        root_meta = root
    else:
        frames, root_meta = [], {}

    # match metadata (for fps/pitch, etc.)
    meta = {}
    if md_path.exists():
        try:
            with open(md_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
        except Exception:
            meta = {}
    # merge any root meta we might want
    if isinstance(root_meta, dict):
        meta = {**root_meta, **meta}

    fps = (
        meta.get("frame_rate") or meta.get("fps") or 10
    )  # SkillCorner OpenData is often 10 fps

    rows = []
    for fr in frames:
        if not isinstance(fr, dict):
            continue

        period = fr.get("period") or fr.get("half")
        frame_no = fr.get("frame") or fr.get("frame_id")
        time_raw = fr.get("timestamp") or fr.get("time") or fr.get("t") or fr.get("ts")

        # parse to seconds; add period offset if available (45 min halves = 2700s)
        secs = _to_seconds(time_raw, frame_no, fps)
        if secs is not None and period is not None:
            try:
                pnum = int(period)
                if pnum >= 1:
                    secs = secs + (pnum - 1) * 2700
            except Exception:
                pass

        ents = (
            fr.get("data")
            or fr.get("entities")
            or fr.get("players")
            or fr.get("objects")
            or []
        )
        if not isinstance(ents, list):
            continue

        for e in ents:
            if not isinstance(e, dict):
                continue
            eid = (
                e.get("id")
                or e.get("entity_id")
                or e.get("player_id")
                or e.get("track_id")
            )
            team = e.get("team_id") or e.get("team") or e.get("teamId") or e.get("tid")

            # coordinates
            x = (
                e.get("x")
                or (isinstance(e.get("position"), dict) and e["position"].get("x"))
                or (
                    isinstance(e.get("coordinates"), dict) and e["coordinates"].get("x")
                )
            )
            y = (
                e.get("y")
                or (isinstance(e.get("position"), dict) and e["position"].get("y"))
                or (
                    isinstance(e.get("coordinates"), dict) and e["coordinates"].get("y")
                )
            )
            speed = e.get("speed") or e.get("v")

            if x is None or y is None:
                continue

            rows.append(
                {
                    "timestamp": secs,
                    "period": period,
                    "frame": frame_no,
                    "entity_id": eid,
                    "team_id": team,
                    "x": x,
                    "y": y,
                    "speed": speed,
                }
            )

    df = pd.DataFrame(rows)

    # type coercion
    for c in ("timestamp", "frame", "x", "y", "speed"):
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    return df, meta


def list_files(root, pattern="*.json"):
    return sorted(Path(root).rglob(pattern))


# -------- StatsBomb via mplsoccer --------
def sb_events(match_id):
    """Return events, related, freeze, tactics for a StatsBomb match_id."""
    from mplsoccer import Sbopen

    parser = Sbopen()
    return parser.event(match_id)


def sb_matches(competition_id, season_id):
    """List matches for convenience."""
    from mplsoccer import Sbopen

    parser = Sbopen()
    return parser.matches(competition_id=competition_id, season_id=season_id)


# -------- Metrica (generic CSV loaders) --------
def metrica_tracking_csv(path):
    """Load a Metrica tracking CSV into a DataFrame."""
    return pd.read_csv(path)


def metrica_events_csv(path):
    """Load a Metrica events CSV into a DataFrame."""
    return pd.read_csv(path)

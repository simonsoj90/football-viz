from mplsoccer import Pitch, VerticalPitch


def make_pitch(
    orientation="h",
    pitch_type="statsbomb",
    pitch_length=None,
    pitch_width=None,
    tight_layout=True,
    figsize=(10, 6),
    top=0.98,
):
    kwargs = dict(pitch_type=pitch_type, line_zorder=2, line_color="#111111")
    if pitch_length is not None and pitch_width is not None:
        kwargs["pitch_length"] = pitch_length
        kwargs["pitch_width"] = pitch_width
    pitch = Pitch(**kwargs) if orientation == "h" else VerticalPitch(**kwargs)
    fig, ax = pitch.draw(tight_layout=tight_layout, figsize=figsize)
    fig.subplots_adjust(top=top)
    return pitch, fig, ax


def add_title(fig, text, fontsize=16):
    fig.suptitle(text, fontsize=fontsize, y=0.99)


def save_fig(fig, out_path, dpi=200):
    fig.savefig(out_path, dpi=dpi, bbox_inches="tight")

def run_glyph_engine(signal):
    if signal in ["SEAL", "GLYPH", "RECURSE"]:
        return f"Glyph Engine received: {signal} — Executing."
    return "Unrecognized signal."
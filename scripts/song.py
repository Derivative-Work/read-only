"""This song's files and stems, in one place for every analysis script."""
TITLE = "Read-Only"
TRACK = f"audio/track/{TITLE}.wav"  # the Suno mix; timing is built on it (the post-filter does not move timing)
MASTER = f"audio/master/{TITLE} (postfilter m6f).wav"
# Suno's stem export names files "<n> <Stem>.wav"; there is no MIDI in this export.
STEMS = ["Lead Vocals", "Backing Vocals", "Drums", "Bass", "Guitar", "Keyboard", "Percussion", "Strings", "Synth", "Other"]


def stem(name):
    return f"audio/stems/{STEMS.index(name)} {name}.wav"

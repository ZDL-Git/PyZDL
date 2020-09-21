import IPython
from IPython.core.display import display


def soundAlert():
    display(IPython.display.Audio("/content/DriveNotebooks/data/audio/Air Horn-SoundBible.com-964603082.mp3",
                                  autoplay=True))

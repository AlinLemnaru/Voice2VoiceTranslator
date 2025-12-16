import tkinter as tk
from dependencies.ui import VoiceToVoiceTranslatorApp


def main():
    root = tk.Tk()
    app = VoiceToVoiceTranslatorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
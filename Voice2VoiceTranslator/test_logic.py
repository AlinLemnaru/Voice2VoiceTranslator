from dependencies.logic import TranslatorService

def main():
    service = TranslatorService()

    def on_status(msg):
        print("[STATUS]", msg)

    def on_source_text(text):
        print("[SOURCE]", text)

    def on_translated_text(text):
        print("[TRANSLATED]", text)

    def on_error(msg):
        print("[ERROR]", msg)

    callbacks = {
        "on_status": on_status,
        "on_source_text": on_source_text,
        "on_translated_text": on_translated_text,
        "on_error": on_error,
    }

    # adapt these to your config: recognition code vs translation code
    source_lang_code = "en"   # for STT
    target_lang_code = "ro"      # for translation/TTS

    service.run_pipeline(source_lang_code, target_lang_code, callbacks)

if __name__ == "__main__":
    main()

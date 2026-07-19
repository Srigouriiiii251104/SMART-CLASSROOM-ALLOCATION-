from django.core.management.base import BaseCommand, CommandError

from accounts.models import User

from assistant_bot.services import respond_to_query


class Command(BaseCommand):
    help = "Run the optional voice assistant interface."

    def handle(self, *args, **options):
        try:
            import pyttsx3
            import speech_recognition as sr
        except ImportError as exc:
            raise CommandError(
                "Voice assistant dependencies are missing. Install requirements-optional.txt first."
            ) from exc

        user = User.objects.filter(role=User.ROLE_ADMIN).first() or User.objects.first()
        if not user:
            raise CommandError("Create at least one user before starting the voice assistant.")

        recognizer = sr.Recognizer()
        speaker = pyttsx3.init()
        self.stdout.write(self.style.SUCCESS("Voice assistant started. Say 'exit' to stop."))

        while True:
            with sr.Microphone() as source:
                self.stdout.write("Listening...")
                audio = recognizer.listen(source)
            try:
                text = recognizer.recognize_google(audio)
            except Exception as exc:  # noqa: BLE001
                self.stdout.write(f"Could not understand audio: {exc}")
                continue

            if text.lower().strip() in {"exit", "quit", "stop"}:
                self.stdout.write("Stopping voice assistant.")
                break

            response = respond_to_query(text, user)
            self.stdout.write(response)
            speaker.say(response)
            speaker.runAndWait()

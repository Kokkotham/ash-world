from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Placeholder for Phase 1 rule data import. Implementation is intentionally deferred.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Rule data import is not implemented in this skeleton step.'))

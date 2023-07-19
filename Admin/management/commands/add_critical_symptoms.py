from django.core.management.base import BaseCommand
from Admin.models import CriticalSymptoms


class Command(BaseCommand):
    help = "To add data to critical symptom"
    def handle(self, *args, **options):
        CriticalSymptoms.objects.bulk_create([
            CriticalSymptoms(name="Bleeding that goes from light to heavy"),
            CriticalSymptoms(name="Weight loss"),
            CriticalSymptoms(name="Tissue that looks like blood clots passing from your vagina"),
            CriticalSymptoms(name="Excessive vomiting"),
            CriticalSymptoms(name="Dehyderation"),
            CriticalSymptoms(name="Cervix incompetency"),
            CriticalSymptoms(name="Scan single vertical less 2"),
            CriticalSymptoms(name="Single vertical more 8"),
            CriticalSymptoms(name="Weight gain"),
            CriticalSymptoms(name="Jaundice"),
            CriticalSymptoms(name="High blood pressure"),
            CriticalSymptoms(name="Eclampsia"),
            CriticalSymptoms(name="High liver value"),
            CriticalSymptoms(name="Iugr"),
            CriticalSymptoms(name="Oligo"),
            CriticalSymptoms(name="Small baby belly"),
            CriticalSymptoms(name="Parents RH"),
            CriticalSymptoms(name="Early Abortion"),
            CriticalSymptoms(name="Hyperemesis gravidarum"),
            CriticalSymptoms(name="Placenta Preveria"),
            CriticalSymptoms(name="Placenta abruption"),
            CriticalSymptoms(name="Preterm"),
            CriticalSymptoms(name="Polyhydramnios"),
            CriticalSymptoms(name="Diabetes"),
            CriticalSymptoms(name="HELLP"),
            CriticalSymptoms(name="PIH"),
            CriticalSymptoms(name="Fluid Leak"),
            CriticalSymptoms(name="low Anemia")
        ], ignore_conflicts=True)
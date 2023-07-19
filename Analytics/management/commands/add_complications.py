from django.core.management.base import BaseCommand
from Analytics.models import Complications


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        Complications.objects.bulk_create([
            Complications(name="early abortion"),
            Complications(name="hyperemesis gravidarum"),
            Complications(name="uti"),
            Complications(name="placenta preveria"),
            Complications(name="placenta abruption"),
            Complications(name="preterm"),
            Complications(name="oligohydramnios"),
            Complications(name="polyhydramnios"),
            Complications(name="diabetes"),
            Complications(name="HELLP"),
            Complications(name="PIH"),
            Complications(name="IUGR"),
            Complications(name="RH Incampatability"),
            Complications(name="cholestatsis"),
            Complications(name="Fluid Leak"),
            Complications(name="Anemia"),
            Complications(name="Yeast Infections"),
            Complications(name="covid"),
            Complications(name="still birth"),
        ])
        print("complications added.!")
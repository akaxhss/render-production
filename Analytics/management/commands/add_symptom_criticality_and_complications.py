# from unicodedata import category
# from django.core.management.base import BaseCommand
# from Analytics.models import MedicalHistory, Complications


# class Command(BaseCommand):
#     def handle(self, *args, **kwargs):
#        early_abortion =  Complications.objects.get(name__iexact="early abortion")
#        hyperemesis_gravidarum =  Complications.objects.get(name__iexact="hyperemesis gravidarum")
#        uti =  Complications.objects.get(name__iexact="uti")
#        placenta_preveria =  Complications.objects.get(name__iexact="placenta preveria")
#        placenta_abruption =  Complications.objects.get(name__iexact="placenta abruption")
#        preterm =  Complications.objects.get(name__iexact="preterm")
#        oligohydramnios =  Complications.objects.get(name__iexact="oligohydramnios")
#        polyhydramnios =  Complications.objects.get(name__iexact="polyhydramnios")
#        diabetes =  Complications.objects.get(name__iexact="diabetes")
#        hellp =  Complications.objects.get(name__iexact="HELLP")
#        pih =  Complications.objects.get(name__iexact="PIH")
#        iugr =  Complications.objects.get(name__iexact="IUGR")
#        rh_incampatability =  Complications.objects.get(name__iexact="RH Incampatability")
#        fluid_leak =  Complications.objects.get(name__iexact="Fluid Leak")
#        anemia =  Complications.objects.get(name__iexact="Anemia")
#        yeast_infections =  Complications.objects.get(name__iexact="Yeast Infections")
#        covid =  Complications.objects.get(name__iexact="covid")
#        still_birth =  Complications.objects.get(name__iexact="still birth")
#        cholestatsis =  Complications.objects.get(name__iexact="cholestatsis")


#         #infertility treatment
#        infertility_treatment = MedicalHistory.objects.create(name="infertility treatment", category=MedicalHistory.MEDICAL_HISTORY)
#        infertility_treatment.complication.add(early_abortion)
#        infertility_treatment.complication.add(oligohydramnios)
#        infertility_treatment.complication.add(iugr)

     
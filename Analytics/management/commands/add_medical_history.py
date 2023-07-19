from unicodedata import category
from django.core.management.base import BaseCommand
from Analytics.models import MedicalHistory, Complications


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
       early_abortion =  Complications.objects.get(name__iexact="early abortion")
       hyperemesis_gravidarum =  Complications.objects.get(name__iexact="hyperemesis gravidarum")
       uti =  Complications.objects.get(name__iexact="uti")
       placenta_preveria =  Complications.objects.get(name__iexact="placenta preveria")
       placenta_abruption =  Complications.objects.get(name__iexact="placenta abruption")
       preterm =  Complications.objects.get(name__iexact="preterm")
       oligohydramnios =  Complications.objects.get(name__iexact="oligohydramnios")
       polyhydramnios =  Complications.objects.get(name__iexact="polyhydramnios")
       diabetes =  Complications.objects.get(name__iexact="diabetes")
       hellp =  Complications.objects.get(name__iexact="HELLP")
       pih =  Complications.objects.get(name__iexact="PIH")
       iugr =  Complications.objects.get(name__iexact="IUGR")
       rh_incampatability =  Complications.objects.get(name__iexact="RH Incampatability")
       fluid_leak =  Complications.objects.get(name__iexact="Fluid Leak")
       anemia =  Complications.objects.get(name__iexact="Anemia")
       yeast_infections =  Complications.objects.get(name__iexact="Yeast Infections")
       covid =  Complications.objects.get(name__iexact="covid")
       still_birth =  Complications.objects.get(name__iexact="still birth")
       cholestatsis =  Complications.objects.get(name__iexact="cholestatsis")


        #infertility treatment
       infertility_treatment = MedicalHistory.objects.create(name="infertility treatment", category=MedicalHistory.MEDICAL_HISTORY)
       infertility_treatment.complication.add(early_abortion)
       infertility_treatment.complication.add(oligohydramnios)
       infertility_treatment.complication.add(iugr)

       #previous miscariage
       previous_miscariage = MedicalHistory.objects.create(name="previous miscariage", category=MedicalHistory.MEDICAL_HISTORY)
       previous_miscariage.complication.add(early_abortion)
       previous_miscariage.complication.add(oligohydramnios)
       previous_miscariage.complication.add(iugr)

       #multiple pregnancy
       multiple_pregnancy = MedicalHistory.objects.create(name="multiple pregnancy", category=MedicalHistory.MEDICAL_HISTORY)
       multiple_pregnancy.complication.add(hyperemesis_gravidarum)
       multiple_pregnancy.complication.add(placenta_abruption)
       multiple_pregnancy.complication.add(preterm)
       multiple_pregnancy.complication.add(oligohydramnios)
       multiple_pregnancy.complication.add(polyhydramnios)
       multiple_pregnancy.complication.add(pih)
       multiple_pregnancy.complication.add(cholestatsis)

       #Kidney Related Issues
       kidney_related_issues = MedicalHistory.objects.create(name="kidney related issues", category=MedicalHistory.MEDICAL_HISTORY)
       kidney_related_issues.complication.add(uti)
       kidney_related_issues.complication.add(hellp)

       #frequent_uti
       frequent_uti = MedicalHistory.objects.create(name="frequent uti", category=MedicalHistory.MEDICAL_HISTORY)
       frequent_uti.complication.add(uti)

       #hypertension
       hypertension = MedicalHistory.objects.create(name="hypertension", category=MedicalHistory.MEDICAL_HISTORY)
       hypertension.complication.add(placenta_abruption)
       hypertension.complication.add(hellp)
       hypertension.complication.add(pih)

       #fibroids
       Fibroids = MedicalHistory.objects.create(name="fibroids", category=MedicalHistory.MEDICAL_HISTORY)
       Fibroids.complication.add(uti)
       Fibroids.complication.add(placenta_preveria)
       Fibroids.complication.add(placenta_abruption)
       Fibroids.complication.add(preterm)
       Fibroids.complication.add(oligohydramnios)
       Fibroids.complication.add(iugr)

       #pcod
       Pcod = MedicalHistory.objects.create(name="pcod", category=MedicalHistory.MEDICAL_HISTORY)
       Pcod.complication.add(early_abortion)
       Pcod.complication.add(oligohydramnios)
       Pcod.complication.add(iugr)

       #History of ceaserean
       History_of_ceaserean = MedicalHistory.objects.create(name="History of ceaserean", category=MedicalHistory.MEDICAL_HISTORY)
       History_of_ceaserean.complication.add(uti)
       History_of_ceaserean.complication.add(placenta_preveria)

        #History of choleostatsis
       History_of_choleostatsis = MedicalHistory.objects.create(name="History of choleostatsis", category=MedicalHistory.MEDICAL_HISTORY)
       History_of_choleostatsis.complication.add(cholestatsis)

      # ltf_abnormal
       Ltf_abnormal = MedicalHistory.objects.create(name="ltf abnormal", category=MedicalHistory.MEDICAL_HISTORY)
       Ltf_abnormal.complication.add(cholestatsis)
      
      # diabetic
       diabetic = MedicalHistory.objects.create(name="Diabetic", category=MedicalHistory.MEDICAL_HISTORY)
       diabetic.complication.add(polyhydramnios)
       diabetic.complication.add(diabetes)
       diabetic.complication.add(yeast_infections)

      # bp
       Bp = MedicalHistory.objects.create(name="Bp", category=MedicalHistory.MEDICAL_HISTORY)
       Bp.complication.add(hellp)

      # preterm
       Preterm = MedicalHistory.objects.create(name="preterm", category=MedicalHistory.MEDICAL_HISTORY)
       Preterm.complication.add(preterm)

      # Early Abortion
       Early_abortion = MedicalHistory.objects.create(name="early abortion", category=MedicalHistory.MEDICAL_HISTORY)
       Early_abortion.complication.add(iugr)

      # hyperemesis gravidarum
       Hyperemesis_gravidarum = MedicalHistory.objects.create(name="hyperemesis gravidarum", category=MedicalHistory.MEDICAL_HISTORY)
       Hyperemesis_gravidarum.complication.add(hyperemesis_gravidarum)

       # uti
       Uti = MedicalHistory.objects.create(name="uti", category=MedicalHistory.MEDICAL_HISTORY)


      # Placenta preveria
       Placenta_preveria = MedicalHistory.objects.create(name="Placenta preveria", category=MedicalHistory.MEDICAL_HISTORY)
       Placenta_preveria.complication.add(placenta_preveria)

      # Placenta preveria
       Placenta_abruption = MedicalHistory.objects.create(name="Placenta abruption", category=MedicalHistory.MEDICAL_HISTORY)
       Placenta_abruption.complication.add(placenta_abruption)

       # oligohydramnios
       Oligohydramnios = MedicalHistory.objects.create(name="oligohydramnios", category=MedicalHistory.MEDICAL_HISTORY)
       Oligohydramnios.complication.add(preterm)
       Oligohydramnios.complication.add(iugr)

       # polyhydramnios
       Polyhydramnios = MedicalHistory.objects.create(name="polyhydramnios", category=MedicalHistory.MEDICAL_HISTORY)
       Polyhydramnios.complication.add(preterm)
       Polyhydramnios.complication.add(pih)

       # hellp
       Hellp = MedicalHistory.objects.create(name="hellp", category=MedicalHistory.MEDICAL_HISTORY)
       Hellp.complication.add(placenta_abruption)
       Hellp.complication.add(hellp)

       # pih
       Pih = MedicalHistory.objects.create(name="PIH", category=MedicalHistory.MEDICAL_HISTORY)
       Pih.complication.add(placenta_abruption)
       Pih.complication.add(preterm)
       Pih.complication.add(oligohydramnios)
       Pih.complication.add(hellp)
       Pih.complication.add(pih)
       Pih.complication.add(iugr)

      # iugr
       Iugr = MedicalHistory.objects.create(name="iugr", category=MedicalHistory.MEDICAL_HISTORY)
       Iugr.complication.add(preterm)
       Iugr.complication.add(oligohydramnios)
       Iugr.complication.add(pih)
       Iugr.complication.add(iugr)
      
      # cholestatsis
       cholestatsis = MedicalHistory.objects.create(name="cholestatsis", category=MedicalHistory.MEDICAL_HISTORY)
      
      # Fluid Leak
       Fluid_Leak = MedicalHistory.objects.create(name="Fluid Leak", category=MedicalHistory.MEDICAL_HISTORY)
       Fluid_Leak.complication.add(placenta_abruption)

      # Anemia
       Anemia = MedicalHistory.objects.create(name="Anemia", category=MedicalHistory.MEDICAL_HISTORY)
       Anemia.complication.add(iugr)
       Anemia.complication.add(anemia)

      # still birth
       Still_birth = MedicalHistory.objects.create(name="Still Birth", category=MedicalHistory.MEDICAL_HISTORY)
       Still_birth.complication.add(still_birth)
      
      # Thyroid
       Thyroid = MedicalHistory.objects.create(name="Thyroid", category=MedicalHistory.MEDICAL_HISTORY)

    #familt history

       Diabetic = MedicalHistory.objects.create(name='diabetics', category=MedicalHistory.FAMILY_HISTORY)
       Diabetic.complication.add(yeast_infections)
       Diabetic.complication.add(polyhydramnios)
       Diabetic.complication.add(diabetes)

    # Thyroid
       Thyroid = MedicalHistory.objects.create(name='thyroid', category=MedicalHistory.FAMILY_HISTORY)

    # BP
       Bp = MedicalHistory.objects.create(name='bp', category=MedicalHistory.FAMILY_HISTORY)
       Bp.complication.add(hellp)

    # preterm
       Preterm = MedicalHistory.objects.create(name="Preterm", category=MedicalHistory.FAMILY_HISTORY)
       Preterm.complication.add(preterm)

    # Early Abortion
       Early_Abortion = MedicalHistory.objects.create(name="Early Abortion", category=MedicalHistory.FAMILY_HISTORY)
       Early_Abortion.complication.add(iugr)

    # hyperemesis gravidarum
       Hyperemesis_Gravidarum = MedicalHistory.objects.create(name="Hyperemesis Gravidarum", category=MedicalHistory.FAMILY_HISTORY)
       Hyperemesis_Gravidarum.complication.add(hyperemesis_gravidarum)
    
    # uti
       Uti = MedicalHistory.objects.create(name="UTI", category=MedicalHistory.FAMILY_HISTORY)

    # Placenta Preveria
       Placenta_Preveria = MedicalHistory.objects.create(name="Placenta Preveria", category=MedicalHistory.FAMILY_HISTORY)
       Placenta_Preveria.complication.add(placenta_preveria)

    # Placenta abruption
       Placenta_Preveria = MedicalHistory.objects.create(name="Placenta abruption", category=MedicalHistory.FAMILY_HISTORY)
       Placenta_Preveria.complication.add(placenta_abruption)
    
    # Oligohydramnios
       Oligohydramnios = MedicalHistory.objects.create(name="Oligohydramnios", category=MedicalHistory.FAMILY_HISTORY)
       Oligohydramnios.complication.add(preterm)
       Oligohydramnios.complication.add(iugr)


    # Polyhydramnios
       Polyhydramnios = MedicalHistory.objects.create(name="Polyhydramnios", category=MedicalHistory.FAMILY_HISTORY)
       Polyhydramnios.complication.add(preterm)
       Polyhydramnios.complication.add(pih)

    # HELLP
       Hellp = MedicalHistory.objects.create(name="HELLP", category=MedicalHistory.FAMILY_HISTORY)
       Hellp.complication.add(placenta_abruption)
       Hellp.complication.add(hellp)

    # PIH
       Pih = MedicalHistory.objects.create(name="PIH", category=MedicalHistory.FAMILY_HISTORY)
       Pih.complication.add(placenta_abruption)
       Pih.complication.add(preterm)
       Pih.complication.add(oligohydramnios)
       Pih.complication.add(hellp)
       Pih.complication.add(pih)
       Pih.complication.add(iugr)

    # iugr
       Iugr = MedicalHistory.objects.create(name="IUGR", category=MedicalHistory.FAMILY_HISTORY)
       Iugr.complication.add(preterm)
       Iugr.complication.add(oligohydramnios)
       Iugr.complication.add(pih)
       Iugr.complication.add(iugr)
    
    # cholestatsis
       Cholestatsis = MedicalHistory.objects.create(name="Cholestatsis", category=MedicalHistory.FAMILY_HISTORY)

    # Fluid Leak
       Fluid_Leak = MedicalHistory.objects.create(name="Fluid Leak", category=MedicalHistory.FAMILY_HISTORY)
       Fluid_Leak.complication.add(placenta_abruption)

    # Anemia
       Anemia = MedicalHistory.objects.create(name="Anemia", category=MedicalHistory.FAMILY_HISTORY)
       Anemia.complication.add(iugr)
       Anemia.complication.add(anemia)

    # Still Birth
       Still_Birth = MedicalHistory.objects.create(name="Still Birth", category=MedicalHistory.FAMILY_HISTORY)
       Still_Birth.complication.add(still_birth)

    # life style
        # Drugs
       Drugs = MedicalHistory.objects.create(name="Drugs", category=MedicalHistory.LIFE_STYLE)
       Drugs.complication.add(early_abortion)
       Drugs.complication.add(placenta_preveria)
       Drugs.complication.add(placenta_abruption)
       Drugs.complication.add(preterm)
       Drugs.complication.add(oligohydramnios)
       Drugs.complication.add(hellp)
       Drugs.complication.add(iugr)

    # Alcohol
       Alcohol = MedicalHistory.objects.create(name="Alcohol", category=MedicalHistory.LIFE_STYLE)
       Alcohol.complication.add(early_abortion)
       Alcohol.complication.add(placenta_abruption)
       Alcohol.complication.add(placenta_preveria)
       Alcohol.complication.add(preterm)
       Alcohol.complication.add(oligohydramnios)
       Alcohol.complication.add(iugr)

    # Caffeine Intake
       Caffeine_Intake = MedicalHistory.objects.create(name="Caffeine Intake", category=MedicalHistory.LIFE_STYLE)

    print("Done")












        

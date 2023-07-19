from django.contrib import admin
from .models import *

# diet
admin.site.register(BabyPics)


admin.site.register(Meal)
admin.site.register(DietTracker)

# medicine
admin.site.register(MedicineTime)
admin.site.register(Medicines)

# admin.site.register(TakenMedicine)

# # activity
# admin.site.register(ActivityTracker)
# admin.site.register(CustomActivities)


# # symptoms
admin.site.register(SymptomsCategory)
admin.site.register(SymptomsInput)
admin.site.register(PositiveSymptoms)
admin.site.register(PositiveCustomSymptoms)
admin.site.register(Symptoms)

# # exercise
# admin.site.register(Exercise)

# # medical
admin.site.register(Medical)

# # contraction
admin.site.register(Contraction)
admin.site.register(PainScale)

# # client baby Foetal Image
# admin.site.register(BabyPics)


admin.site.register(LastUpdateDate)

admin.site.register(DailyTrackerModule)
admin.site.register(ActivityMainModule)
admin.site.register(ActivitySubModules)

# admin.site.register(ActivitySubModules)
admin.site.register(CustomActivity)
admin.site.register(CompletedCustomActivity)


# Exercises
admin.site.register(Exercises)
admin.site.register(ExerciseVideos)
admin.site.register(CompletedExercises)
admin.site.register(CompletedCustomeExercises)


admin.site.register(CaloriesBurnt)
admin.site.register(ExerciseConsent)
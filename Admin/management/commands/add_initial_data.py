from django.core.management.base import BaseCommand
from LearnIt.models import Modules, Stage
from Customer.models import Meal, MedicineTime, DailyTrackerModule
from Payments.models import MembershipPlans
from Sales.models import CallResponses


class Command(BaseCommand):
    help = "To add data to the single coloumn tables that are later refernced as primary key"
    def handle(self, *args, **options):
        Modules.objects.bulk_create([
            Modules(name='meditation'),
            Modules(name='stay fit'),
            Modules(name='diet'),
            Modules(name='relaxation'),
            Modules(name='test module')
        ], ignore_conflicts=True)
        Stage.objects.bulk_create([
            Stage(name='stage1'),
            Stage(name='stage2'),
            Stage(name='stage3'),
            Stage(name='stage4'),
            Stage(name='stage5'),
            Stage(name='stage6'),
            Stage(name='stage7'),
            Stage(name='stage8'),
            Stage(name='stage9'),
            Stage(name='stage10'),
        ], ignore_conflicts=True)
        Meal.objects.bulk_create([
            Meal(name='dinner drink'),
            Meal(name='dinner'),
            Meal(name='afternoon snack'),
            Meal(name='lunch'),
            Meal(name='mid day snack'),
            Meal(name='breakfast'),
            Meal(name='early morning'),
        ], ignore_conflicts=True)
        MedicineTime.objects.bulk_create([
            MedicineTime(name='night after food'),
            MedicineTime(name='night before food'),
            MedicineTime(name='afternoon after food'),
            MedicineTime(name='afternoon before food'),
            MedicineTime(name='morning after food'),
            MedicineTime(name='morning before food')
        ], ignore_conflicts=True)
        DailyTrackerModule.objects.bulk_create([
            DailyTrackerModule(name='activity'),
            DailyTrackerModule(name='exercise')
        ], ignore_conflicts=True)
        MembershipPlans.objects.bulk_create([
            MembershipPlans(name='basic', validity=90, amount=2500),
            MembershipPlans(name='basic', validity=30, amount=1500),
            MembershipPlans(name='basic', validity=280, amount=3000),
            MembershipPlans(name='standard', validity=280, amount=10000)
        ], ignore_conflicts=True)
        CallResponses.objects.bulk_create([
            CallResponses(response="didn't respond"),
            CallResponses(response="didn't called"),
            CallResponses(response="called")
        ], ignore_conflicts=True)



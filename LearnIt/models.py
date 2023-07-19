from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model() 


# Learning module
class Modules(models.Model):
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Learnit module'
    


class Stage(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name



class Videos(models.Model):
    module = models.ForeignKey(Modules, on_delete=models.CASCADE)
    stage = models.ForeignKey(Stage, on_delete=models.CASCADE)
    video = models.FileField(upload_to='videos/', null=True,blank=True)
    url = models.URLField(null=True,blank=True)
    faq = models.TextField(null=True, blank=True)   
    relatedPost = models.TextField(null=True, blank=True)   

    class Meta:
        unique_together = ['stage', 'module']
    
    def __str__(self):
        return self.module.name + ' ' + self.stage.name


class Notes(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    stage = models.ForeignKey(Stage, on_delete=models.CASCADE)
    module = models.ForeignKey(Modules, on_delete=models.CASCADE)

    notes = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.customer.firstname + "'s note - "  + self.notes

    class Meta:
        unique_together = ['customer', 'stage', 'module']
from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.
class CustomUser(AbstractUser):
    viewpassword = models.CharField(max_length=150, blank=True)
    usertype = models.CharField(max_length=50, default='voter')
    status = models.CharField(max_length=50, default='pending')
class Candidate(models.Model):    
    loginid=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    name=models.CharField(max_length=100)
    party=models.CharField(max_length=100)
    dob=models.DateField(null=True)
    address=models.TextField()
    voterid=models.CharField(max_length=100,null=True)
    proof=models.ImageField(upload_to='candidate_proofs/',null=True)
    photo=models.ImageField(upload_to='candidate_photos/')
    symbol=models.ImageField(upload_to='candidate_symbols/')
class Voter(models.Model):
    loginid=models.ForeignKey(CustomUser,on_delete=models.CASCADE)
    name=models.CharField(max_length=100)
    dob=models.DateField(null=True)
    email=models.EmailField(null=True)
    address=models.TextField()
    photo=models.ImageField(upload_to='voter_photos/')
    voterid=models.CharField(max_length=100)
    voteridproof=models.ImageField(upload_to='voter_id_proofs/')
class Election(models.Model):
    electionname=models.CharField(max_length=200)
    dateofelection=models.DateField()
    description=models.TextField()
    status=models.CharField(max_length=50,default='pending')




from django.utils.timezone import now
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from uuid import uuid4

from baham.constants import COLOURS, TOWNS
from baham.enum_types import VehicleType, VehicleStatus, UserType


# Custom validators
def validate_colour(value):
    '''
    Validate that the value exists in the list of available colours
    '''
    return value.upper() in COLOURS


# Create your models here.
class UserProfile(models.Model):
    # Should have one-to-one relationship with Django user
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    birthdate = models.DateField()
    gender = models.CharField(max_length=1, choices=[('M', 'Male'), ('F', 'Female')])
    type = models.CharField(max_length=10, choices=[(t.name, t.value) for t in UserType])
    primary_contact = models.CharField(max_length=20, null=False, blank=False)
    alternate_contact = models.CharField(max_length=20, null=True)
    address = models.CharField(max_length=255)
    address_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    address_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True)
    landmark = models.CharField(max_length=255, null=False)
    town = models.CharField(max_length=50, null=False, choices=[(c, c) for c in TOWNS])
    active = models.BooleanField(default=True, editable=False)
    date_deactivated = models.DateTimeField(editable=False, null=True)
    bio = models.TextField()
    # ACTIVITY #3
    date_created = models.DateTimeField(default=timezone.now, null=False, editable=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, default=1, null=True, editable=False, related_name='userprofile_creator')
    date_updated = models.DateTimeField(null=True)
    updated_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name='userprofile_updater')
    voided = models.BooleanField(default=False, null=False)
    date_voided = models.DateTimeField(null=True)
    voided_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name='userprofile_voider')
    void_reason = models.CharField(null=True, max_length=1024)
    uuid = models.UUIDField(default=uuid4, editable=False, unique=True)

    def __str__(self):
        return f"{self.username} {self.first_name} {self.last_name}"
    
    def update(self, updated_by=None, *args, **kwargs):
        self.date_updated = timezone.now()
        if (not updated_by):
            updated_by = User.objects.get(pk=1)
        self.updated_by = updated_by
        self.save()
    
    def delete(self, voided_by=None, *args, **kwargs):
        self.voided = True
        self.date_voided = timezone.now()
        if (not self.void_reason):
            self.void_reason = 'Voided without providing a reason'
        if (not voided_by):
            voided_by = User.objects.get(pk=1)
        self.voided_by = voided_by
        self.save()
    
    def undelete(self, *args, **kwargs):
        if self.voided:
            self.voided = False
            self.date_voided = None
            self.void_reason = None
            self.voided_by = None
            self.save()
    
    def purge(self, *args, **kwargs):
        self.delete()


class VehicleModel(models.Model):
    model_id = models.AutoField(primary_key=True, db_column='id')
    # Toyota, Honda, Suzuki, Kia, etc.
    vendor = models.CharField(max_length=20, null=False, blank=False)
    # Corolla, Vitz, City, Sportage, etc.
    model = models.CharField(max_length=20, null=False, blank=False, default='Unknown')
    # Sedan, Motorcyle, SUV, Van, etc.
    type = models.CharField(max_length=50, choices=[(t.name, t.value) for t in VehicleType],
                            help_text="Select the vehicle chassis type")
    # Sitting capacity
    capacity = models.PositiveSmallIntegerField(null=False, default=2)

    is_voided = models.BooleanField(default=False)
    date_voided = models.DateTimeField(null=True)
    void_reason = models.CharField(null=True, max_length=1024)
    uuid = models.UUIDField(default=uuid4, editable=False, unique=True)

    date_created = models.DateTimeField(default=timezone.now, null=False, editable=False)
    date_updated = models.DateTimeField(null=True)

    created_by = models.ForeignKey(User, on_delete=models.CASCADE, default=1, null=False, editable=False, related_name='vehiclemodel_creator')
    updated_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name='vehiclemodel_updater')
    voided_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name='vehiclemodel_voider')


    def void(self, voided_by=None):
        self.is_voided = True
        self.date_voided = timezone.now()
        if (not voided_by):
            voided_by = User.objects.get(pk=1)
        self.voided_by = voided_by

        self.save()

    def unvoid(self):
        self.is_voided = False
        self.date_voided = None
        self.void_reason = None
        self.voided_by = None
        self.save()

    class Meta:
        db_table = "baham_vehicle_model"

    def __str__(self):
        return f"{self.vendor} {self.model}"


class Vehicle(models.Model):
    vehicle_id = models.AutoField(primary_key=True, db_column='id')
    # ABC-877
    registration_number = models.CharField(max_length=10, unique=True, null=False, blank=False,
                                           help_text="Unique registration/license plate no. of the vehicle.")
    colour = models.CharField(max_length=50, default='white', validators=[validate_colour])
    model = models.ForeignKey(VehicleModel, null=False, on_delete=models.CASCADE)
    owner = models.ForeignKey(User, null=False, on_delete=models.CASCADE)
    status = models.CharField(max_length=50, choices=[(t.name, t.value) for t in VehicleStatus])
    picture1 = models.ImageField(upload_to='pictures', null=True)
    picture2 = models.ImageField(upload_to='pictures', null=True)
    # ACTIVITY #3
    updated_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name='vehicle_updater')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, default=1, null=False, editable=False, related_name='vehicle_creator')
    date_updated = models.DateTimeField(null=True)
    date_voided = models.DateTimeField(null=True)
    voided = models.BooleanField(default=False, null=False)
    void_reason = models.CharField(null=True, max_length=1024)
    date_created = models.DateTimeField(default=timezone.now, null=False, editable=False)
    uuid = models.UUIDField(default=uuid4, editable=False, unique=True)
    voided_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name='vehicle_voider')

    def __str__(self):
        return f"{self.model.vendor} {self.model.model} {self.colour}"
   
    def delete(self, voided_by=None, *args, **kwargs):
        self.voided = True
        self.date_voided = timezone.now()
        if (not self.void_reason):
            self.void_reason = "VOIDED BY USER"
        if (not voided_by):
            voided_by = User.objects.get(pk=1)
        self.voided_by = voided_by
        self.save()
    
    def undelete(self, *args, **kwargs):
        if self.voided:
            self.voided = False
            self.date_voided = None
            self.void_reason = None
            self.voided_by = None
            self.save()
    


class Contract(models.Model):
    contract_id = models.AutoField(primary_key=True, db_column='id')
    vehicle = models.ForeignKey(Vehicle, null=False, on_delete=models.CASCADE)
    companion = models.ForeignKey(UserProfile, null=False, on_delete=models.CASCADE)
    effective_start_date = models.DateField(null=False)
    expiry_date = models.DateField()
    is_active = models.BooleanField(default=True)
    fuel_share = models.PositiveSmallIntegerField(help_text="Percentage of fuel contribution.")
    maintenance_share = models.PositiveSmallIntegerField(help_text="Percentage of maintenance cost contribution.")
    schedule = models.CharField(max_length=255, null=False)  #TODO: use Django Scheduler
    # ACTIVITY #3
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, default=1, null=False, editable=False, related_name='contract_creator')
    updated_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name='contract_updater')
    date_voided = models.DateTimeField(null=True)
    date_created = models.DateTimeField(default=timezone.now, null=False, editable=False)
    voided = models.BooleanField(default=False, null=False)
    voided_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name='contract_voider')
    date_updated = models.DateTimeField(null=True)
    uuid = models.UUIDField(default=uuid4, editable=False, unique=True)
    void_reason = models.CharField(null=True, max_length=1024)
    
    def __str__(self):
        return f"{self}" # TODO: Complete this
    
    def update(self, updated_by=None, *args, **kwargs):
        self.date_updated = timezone.now()
        if (not updated_by):
            updated_by = User.objects.get(pk=1)
        self.updated_by = updated_by
        self.save()
    
    def delete(self, voided_by=None, *args, **kwargs):
        self.voided = True
        self.date_voided = timezone.now()
        if (not self.void_reason):
            self.void_reason = 'No Reason'
        if (not voided_by):
            voided_by = User.objects.get(pk=1)
        self.voided_by = voided_by
        self.save()
    
    def undelete(self, *args, **kwargs):
        if self.voided:
            self.voided = False
            self.date_voided = None
            self.void_reason = None
            self.voided_by = None
            self.save()


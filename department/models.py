from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


from authentication.models import User
# Create your models here.


def get_department_dir(instance, filename):
    return 'departments/' + instance.name + '/' + filename

# department is designed for static webpage and edited by admin


class Department(models.Model):
    name = models.CharField(_('Department name'),
                            max_length=80, primary_key=True)
    phone = models.CharField(_('Department Phone No'), max_length=14)
    email = models.EmailField(_('Department Email'), unique=True)
    dean = models.OneToOneField(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='dean_name')
    msg = models.CharField(_('Dean Msg'), max_length=512,
                           null=True, blank=True)

    def __str__(self):
        return self.name

    @property
    def no_of_staffs(self):
        today = timezone.now().date()
        return self.departmentpays_set.filter(user_usertype__exact='sf', enddate__gte=today).count()

    @property
    def no_of_teachers(self):
        today = timezone.now().date()
        return self.departmentpays_set.filter(user_usertype__exact='tr', enddate__gte=today).count()


def get_department_dir(instance, filename):
    return instance.department.name + '/' + filename


class DepartmentPhotos(models.Model):
    department = models.ForeignKey(
        Department, on_delete=models.CASCADE, related_name='department_photos')
    image = models.ImageField(_('Department Image'),
                              upload_to=get_department_dir, blank=False, null=False)

    def __str__(self):
        return self.department.name


class Sections(models.Model):
    name = models.CharField(_('Section name'), max_length=80, primary_key=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    description = models.CharField(
        _('Section description'), max_length=512, null=True, blank=True)

    class Meta:
        unique_together = ('name', 'department')

    def __str__(self):
        return self.name + ' - ' + self.department.name


class DepartmentAssigns(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    amount = models.IntegerField(_('Amount'), null=False)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    enddate = models.DateField(_('Assigned End Date'), null=False)
    assigned_date = models.DateField(
        _('Assigned Date'), null=False, blank=True, default=timezone.now)

    class Meta:
        unique_together = ('department', 'user')

    def __str__(self):
        return str(self.department) + ' ' + str(self.amount)

    # @property
    # def salaryperiod(self):
    #     for i in self.PERIOD_CHOICES:
    #         if i[0] == self._salaryperiod:
    #             return i[1]

    # @salaryperiod.setter
    # def salaryperiod(self, value):
    #     for i in self.PERIOD_CHOICES:
    #         if i[1] == value:
    #             self._salaryperiod = i[0]
    #             return

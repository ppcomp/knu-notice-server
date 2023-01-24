from django.db import models


class Version(models.Model):
    def __str__(self):
        return f'{self.latest} - {self.available_version_code}'
    latest = models.CharField(max_length=20)
    available_version_code = models.IntegerField(default=0)


class BoardInfo(models.Model):
    class Meta:
        db_table = 'board_info'

    id = models.AutoField(primary_key=True)
    code = models.CharField(unique=True, max_length=50)
    api_path = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    start_url = models.CharField(max_length=300)
    model = models.CharField(max_length=50)
    bid_param = models.CharField(max_length=20, null=True)
    page_param = models.CharField(max_length=20, null=True)
    fixed_xpath = models.CharField(max_length=300)
    url_xpath = models.CharField(max_length=300)
    title_xpath = models.CharField(max_length=300)
    date_xpath = models.CharField(max_length=300, null=True)
    author_xpath = models.CharField(max_length=300, null=True)
    reference_xpath = models.CharField(max_length=300, null=True)
    inside_date_xpath = models.CharField(max_length=300, null=True)
    drop_offset = models.IntegerField(default=0)

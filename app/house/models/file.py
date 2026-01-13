from django.db import models

class File(models.Model):
    name = models.CharField(max_length=200, verbose_name="File Name")
    path = models.TextField(verbose_name="File Path")
    signature = models.CharField(max_length=64, verbose_name="File signature")

    size = models.PositiveIntegerField(
        default=0,
        #validators=[MinValueValidator(0), MaxValueValidator(130)],
        null=False,
        blank=False,
    )
    views_count = models.PositiveIntegerField(
        default=0,
        null=False,
        blank=False,
    )

    deleted_at = models.DateTimeField() 
    created_at = models.DateTimeField(auto_now_add=True)
    viewed_at = models.DateTimeField() 


    #tags = models.ManyToManyField('Tag', related_name='File', blank=True)
    tags = models.ManyToManyField('Tag', through='FileTag', related_name='File')

    # class Meta:
    #     verbose_name = "Produto"
    #     verbose_name_plural = "Produtos"

    def __str__(self):
        return self.name
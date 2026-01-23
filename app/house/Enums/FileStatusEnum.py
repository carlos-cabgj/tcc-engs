class FileStatusEnum(models.TextChoices):
    ACTIVE   = 'R', 'Vermelho'
    GREEN = 'G', 'Verde'
    BLUE  = 'B', 'Azul'


#status = models.IntegerField(choices=Status.choices, default=Status.PENDING)
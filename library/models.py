from django.db import models
from django.urls import reverse


class Category(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('library:category', kwargs={'category_slug': self.slug})


class Work(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='works')
    name = models.CharField(max_length=200)
    slug = models.SlugField()
    author = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']
        unique_together = ('category', 'slug')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('library:work', kwargs={
            'category_slug': self.category.slug,
            'work_slug': self.slug,
        })


class Section(models.Model):
    work = models.ForeignKey(Work, on_delete=models.CASCADE, related_name='sections')
    reference = models.CharField(
        max_length=200,
        help_text='Human-readable reference, e.g. "Exodus 12:8"',
    )
    slug = models.SlugField(
        help_text='URL-safe identifier, e.g. "exodus-12-8"',
    )
    title = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'reference']
        unique_together = ('work', 'slug')

    def __str__(self):
        return f'{self.work.name} – {self.reference}'

    def get_absolute_url(self):
        return reverse('library:section', kwargs={
            'category_slug': self.work.category.slug,
            'work_slug': self.work.slug,
            'section_slug': self.slug,
        })


class Paragraph(models.Model):
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='paragraphs')
    number = models.PositiveIntegerField()
    hebrew_text = models.TextField()
    english_text = models.TextField()

    class Meta:
        ordering = ['number']
        unique_together = ('section', 'number')

    def __str__(self):
        return f'{self.section} §{self.number}'

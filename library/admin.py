from django.contrib import admin
from .models import Category, Work, Section, Paragraph


class WorkInline(admin.TabularInline):
    model = Work
    extra = 1
    prepopulated_fields = {'slug': ('name',)}


class SectionInline(admin.TabularInline):
    model = Section
    extra = 1
    prepopulated_fields = {'slug': ('reference',)}


class ParagraphInline(admin.TabularInline):
    model = Paragraph
    extra = 0


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'order')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [WorkInline]


@admin.register(Work)
class WorkAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'author', 'order')
    list_filter = ('category',)
    prepopulated_fields = {'slug': ('name',)}
    inlines = [SectionInline]


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ('reference', 'work', 'slug', 'order')
    list_filter = ('work__category', 'work')
    prepopulated_fields = {'slug': ('reference',)}
    inlines = [ParagraphInline]


@admin.register(Paragraph)
class ParagraphAdmin(admin.ModelAdmin):
    list_display = ('number', 'section')
    list_filter = ('section__work__category', 'section__work')

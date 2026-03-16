from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import SectionUploadForm
from .models import Category, Paragraph, Section, Work
from .parsers import parse_chatgpt_output


def index(request):
    categories = Category.objects.prefetch_related('works')
    return render(request, 'library/index.html', {'categories': categories})


def category_view(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    works = category.works.all()
    return render(request, 'library/category.html', {
        'category': category,
        'works': works,
    })


def work_view(request, category_slug, work_slug):
    category = get_object_or_404(Category, slug=category_slug)
    work = get_object_or_404(Work, category=category, slug=work_slug)
    sections = work.sections.all()
    return render(request, 'library/work.html', {
        'category': category,
        'work': work,
        'sections': sections,
    })


def section_view(request, category_slug, work_slug, section_slug):
    category = get_object_or_404(Category, slug=category_slug)
    work = get_object_or_404(Work, category=category, slug=work_slug)
    section = get_object_or_404(Section, work=work, slug=section_slug)
    paragraphs = section.paragraphs.all()

    # Previous / next navigation
    all_sections = list(work.sections.values_list('slug', flat=True))
    current_index = list(all_sections).index(section_slug) if section_slug in all_sections else -1
    prev_section = None
    next_section = None
    if current_index > 0:
        prev_section = work.sections.filter(slug=all_sections[current_index - 1]).first()
    if current_index >= 0 and current_index < len(all_sections) - 1:
        next_section = work.sections.filter(slug=all_sections[current_index + 1]).first()

    return render(request, 'library/section.html', {
        'category': category,
        'work': work,
        'section': section,
        'paragraphs': paragraphs,
        'prev_section': prev_section,
        'next_section': next_section,
    })


@login_required
def upload_section(request):
    if request.method == 'POST':
        form = SectionUploadForm(request.POST)
        if form.is_valid():
            work = form.cleaned_data['work']
            slug = form.cleaned_data['slug']
            reference = form.cleaned_data['reference']
            title = form.cleaned_data.get('title', '')
            order = form.cleaned_data.get('order') or 0
            content = form.cleaned_data['content']
            replace = form.cleaned_data.get('replace_existing', False)

            parsed = parse_chatgpt_output(content)
            if not parsed:
                form.add_error('content', 'No paragraphs could be parsed from the input.')
                return render(request, 'library/upload.html', {'form': form})

            section, created = Section.objects.get_or_create(
                work=work,
                slug=slug,
                defaults={'reference': reference, 'title': title, 'order': order},
            )
            if not created:
                # Update metadata even when replacing
                section.reference = reference
                section.title = title
                section.order = order
                section.save()

            if replace or created:
                if replace and not created:
                    section.paragraphs.all().delete()
                for item in parsed:
                    Paragraph.objects.create(
                        section=section,
                        number=item['number'],
                        hebrew_text=item['hebrew'],
                        english_text=item['english'],
                    )
                verb = 'created' if created else 'updated'
                messages.success(
                    request,
                    f'Section "{reference}" {verb} with {len(parsed)} paragraph(s).',
                )
                return redirect(section.get_absolute_url())
    else:
        form = SectionUploadForm()

    return render(request, 'library/upload.html', {'form': form})

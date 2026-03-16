from django import forms
from .models import Category, Work, Section


def _bs(extra_class=''):
    """Return common Bootstrap form-control widget attrs."""
    return {'class': f'form-control {extra_class}'.strip()}


def _bs_select():
    return {'class': 'form-select'}


class SectionUploadForm(forms.Form):
    """Admin form for uploading a new section from ChatGPT output."""

    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        widget=forms.Select(attrs=_bs_select()),
        help_text='Select an existing category or create one via the admin.',
    )
    work = forms.ModelChoiceField(
        queryset=Work.objects.all(),
        widget=forms.Select(attrs=_bs_select()),
        help_text='The work this section belongs to.',
    )
    reference = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs=_bs()),
        help_text='Human-readable reference, e.g. "Exodus 12:8".',
    )
    slug = forms.SlugField(
        max_length=200,
        widget=forms.TextInput(attrs=_bs()),
        help_text='URL-safe slug, e.g. "exodus-12-8".',
    )
    title = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs=_bs()),
        help_text='Optional display title.',
    )
    order = forms.IntegerField(
        initial=0,
        required=False,
        widget=forms.NumberInput(attrs=_bs()),
        help_text='Sort order within the work (lower numbers appear first).',
    )
    content = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 30, 'class': 'form-control font-monospace'}),
        help_text=(
            'Paste the ChatGPT output here. '
            'Each paragraph should be numbered and contain '
            'an "עברית:" block followed by an "English:" block.'
        ),
    )
    replace_existing = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text=(
            'If checked, any existing paragraphs for this section will be '
            'deleted and replaced with the new content.'
        ),
    )

    def clean(self):
        cleaned = super().clean()
        work = cleaned.get('work')
        slug = cleaned.get('slug')
        replace = cleaned.get('replace_existing')

        if work and slug:
            exists = Section.objects.filter(work=work, slug=slug).exists()
            if exists and not replace:
                raise forms.ValidationError(
                    'A section with this slug already exists for this work. '
                    'Check "Replace existing" to overwrite it.'
                )
        return cleaned

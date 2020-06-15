from django import forms

from main.models import Query

LANGUAGE_CHOICES = (
    ("all", "All"),
    ("ar", "Arabic"),
    ("de", "German"),
    ("en", "English"),
    ("es", "Spanish"),
    ("fr", "Franch"),
    ("he", "Hebrew"),
    ("it", "Italian"),
    ("nl", "Dutch"),
    ("no", "Norwegia"),
    ("pt", "Portuguese"),
    ("ru", "Russian"),
    ("se", "Swedish"),
    ("zh", "Chinese")
)

SORTING_CHOICES = (
    ("publishedAt", "Publishing time"),
    ("relevancy", "Relevancy"),
    ("popularity", "Popularity")
)


class QueryForm(forms.ModelForm):
    # query = forms.CharField(max_length=128)
    # sources = forms.CharField(max_length=128, required=False)
    # domains = forms.CharField(max_length=128, required=False)
    # from_date = forms.DateField(required=False)
    # to_date = forms.DateField(required=False)
    # language = forms.ChoiceField(choices=LANGUAGE_CHOICES, required=False)
    # sorting = forms.ChoiceField(choices=SORTING_CHOICES, required=False)

    class Meta:
        model = Query
        fields = (
            "query",
            "sources",
            "domains",
            "from_date",
            "to_date",
            "language",
            "sorting"
        )

    # def make_query(self):
    #     data = self.cleaned_data
    #
    #     print("Data ", data)

from django import forms

from Post.models import Question, Answer


class QuestionCreationForm(forms.ModelForm):
    tags = forms.CharField(help_text="Add tags separated by commas", required=False)
    class Meta:
        model = Question
        fields = ['title', 'description', 'tags']


class QuestionEditForm(forms.ModelForm):
    tags = forms.CharField(help_text="Add tags separated by commas", required=False)
    class Meta:
        model = Question
        fields = ['title', 'description', 'tags']
    def clean(self):
        cleaned_data = super().clean()

        if not self.cleaned_data['title']:
            cleaned_data['title'] = self.instance.title
        if not self.cleaned_data['description']:
            cleaned_data['description'] = self.instance.description
        if not self.cleaned_data['tags']:
            cleaned_data['tags'] = self.instance.tags
        return cleaned_data

class AnswerCreationForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ['content']


class AnswerEditForm(forms.ModelForm):

    class Meta:
        model = Answer
        fields = ['content']

    def clean(self):
        cleaned_data = super().clean()

        if not self.cleaned_data['content']:
            cleaned_data['content'] = self.instance.content
        return cleaned_data

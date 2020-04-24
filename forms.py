forms.py
========
    from django.forms.formsets import Form, BaseFormSet, formset_factory, \
            ValidationError


    class QuestionForm(Form):
        """Form for a single question on a quiz"""
        def __init__(self, *args, **kwargs):
            # CODE TRICK #1
            # pass in a question from the formset
            # use the question to build the form
            # pop removes from dict, so we don't pass to the parent
            self.question = kwargs.pop('question')
            super(QuestionForm, self).__init__(*args, **kwargs)

            # CODE TRICK #2
            # add a non-declared field to fields
            # use an order_by clause if you care about order
            self.answers = self.question.answer_set.all(
                    ).order_by('id')
            self.fields['answers'] = forms.ModelChoiceField(
                    queryset=self.answers())


    class BaseQuizFormSet(BaseFormSet):
        def __init__(self, *args, **kwargs):
            # CODE TRICK #3 - same as #1:
            # pass in a valid quiz object from the view
            # pop removes arg, so we don't pass to the parent
            self.quiz = kwargs.pop('quiz')

            # CODE TRICK #4
            # set length of extras based on query
            # each question will fill one 'extra' slot
            # use an order_by clause if you care about order
            self.questions = self.quiz.question_set.all().order_by('id')
            self.extra = len(self.questions)
            if not self.extra:
                raise Http404('Badly configured quiz has no questions.')

            # call the parent constructor to finish __init__            
            super(BaseQuizFormSet, self).__init__(*args, **kwargs)

        def _construct_form(self, index, **kwargs):
            # CODE TRICK #5
            # know that _construct_form is where forms get added
            # we can take advantage of this fact to add our forms
            # add custom kwargs, using the index to retrieve a question
            # kwargs will be passed to our form class
            kwargs['question'] = self.questions[index]
            return super(BaseQuizFormSet, self)._construct_form(index, **kwargs)


    QuizFormSet = formset_factory(
        QuestionForm, formset=BaseQuizDynamicFormSet)


views.py
========

from django.http import Http404


    def quiz_form(request, quiz_id):
        try:
            quiz = Quiz.objects.get(pk=quiz_id)
        except Quiz.DoesNotExist:
            return Http404('Invalid quiz id.')
        if request.method == 'POST':
            formset = QuizFormSet(quiz=quiz, data=request.POST)
            answers = []
            if formset.is_valid():
                for form in formset.forms:
                    answers.append(str(int(form.is_correct())))
                return HttpResponseRedirect('%s?a=%s'
                        % (reverse('result-display',args=[quiz_id]), ''.join(answers)))
        else:
            formset = QuizFormSet(quiz=quiz)

        return render_to_response('quiz.html', locals())


template
========

Just change this:
    {% for form in forms %}
to this:
    {% for form in formset.forms %}

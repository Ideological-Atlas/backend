from django.test import TestCase
from ideology.api.views.axis_answer_views import UserAxisAnswerListBySectionView
from ideology.api.views.conditioner_answer_views import (
    UserConditionerAnswerListByComplexityView,
)


class SwaggerFakeViewTestCase(TestCase):
    def test_user_axis_answer_list_swagger(self):
        view = UserAxisAnswerListBySectionView()
        view.swagger_fake_view = True
        view.kwargs = {}
        queryset = view.get_queryset()
        self.assertEqual(list(queryset), [])
        self.assertEqual(queryset.count(), 0)

    def test_user_conditioner_answer_list_swagger(self):
        view = UserConditionerAnswerListByComplexityView()
        view.swagger_fake_view = True
        view.kwargs = {}
        queryset = view.get_queryset()
        self.assertEqual(list(queryset), [])
        self.assertEqual(queryset.count(), 0)

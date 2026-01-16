from core.factories import UserFactory
from django.test import RequestFactory, TestCase
from ideology.api.views.axis_answer_views import UserAxisAnswerListBySectionView
from ideology.api.views.conditioner_answer_views import (
    UserConditionerAnswerListByComplexityView,
)


class SwaggerFakeViewTestCase(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.user = UserFactory()

    def test_user_axis_answer_list_swagger(self):
        view = UserAxisAnswerListBySectionView()
        view.swagger_fake_view = True
        view.kwargs = {}
        view.request = self.factory.get("/")
        view.request.user = self.user

        queryset = view.get_queryset()

        self.assertEqual(list(queryset), [])
        self.assertEqual(queryset.count(), 0)

    def test_user_conditioner_answer_list_swagger(self):
        view = UserConditionerAnswerListByComplexityView()
        view.swagger_fake_view = True
        view.kwargs = {}
        view.request = self.factory.get("/")
        view.request.user = self.user

        queryset = view.get_queryset()

        self.assertEqual(list(queryset), [])
        self.assertEqual(queryset.count(), 0)

from core.exceptions.api_exceptions import BadRequestException, NotFoundException
from core.services.affinity_calculator import AffinityCalculator
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import OpenApiParameter, extend_schema
from ideology.api.serializers import AffinitySerializer, IdeologyAffinitySerializer
from ideology.models import CompletedAnswer, Ideology, UserAxisAnswer
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


class BaseAffinityView(GenericAPIView):
    permission_classes = [AllowAny]

    def get_source_data(self):
        source_uuid = self.request.query_params.get("source_answer_uuid")

        if source_uuid:
            try:
                completed_answer = CompletedAnswer.objects.get(uuid=source_uuid)
                return completed_answer.get_mapped_for_calculation()
            except CompletedAnswer.DoesNotExist:
                raise NotFoundException(_("Source Completed Answer not found."))

        if self.request.user.is_authenticated:
            return UserAxisAnswer.objects.get_mapped_for_calculation(self.request.user)

        raise BadRequestException(
            _(
                "Anonymous users must provide 'source_answer_uuid' or be logged in to calculate affinity."
            )
        )

    def process_affinity_request(
        self, target_object, target_key, target_value=None, explicit_value=False
    ):
        # If explicit_value is True, we use target_value even if it is None (e.g. Anonymous user).
        # Otherwise, fallback to target_object (default behavior for Ideologies).
        final_target_value = (
            target_value if explicit_value or target_value else target_object
        )

        source_data = self.get_source_data()
        target_data = target_object.get_mapped_for_calculation()

        calculation = AffinityCalculator(source_data, target_data).calculate_detailed()
        hydrated = AffinityCalculator.hydrate_affinity_structure(calculation)

        response_data = {
            target_key: final_target_value,
            "total": hydrated["total"],  # FIX: Key must match serializer source="total"
            "complexities": hydrated["complexities"],
        }
        serializer = self.get_serializer(response_data)
        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(
    tags=["ideologies"],
    summary=_("Calculate affinity with an Ideology"),
    description=_(
        "Calculates the ideological affinity (0-100%) between a source (Authenticated User or CompletedAnswer UUID) "
        "and a target Ideology."
    ),
    parameters=[
        OpenApiParameter(
            name="source_answer_uuid",
            description=_("UUID of the source CompletedAnswer (required if anonymous)"),
            required=False,
            type=str,
            location=OpenApiParameter.QUERY,
        ),
        OpenApiParameter(
            name="ideology_uuid",
            location=OpenApiParameter.PATH,
            description="UUID of the target Ideology",
            required=True,
            type=str,
        ),
    ],
    responses={200: IdeologyAffinitySerializer},
)
class IdeologyAffinityView(BaseAffinityView):
    serializer_class = IdeologyAffinitySerializer
    queryset = Ideology.objects.all()
    lookup_field = "uuid"
    lookup_url_kwarg = "ideology_uuid"

    def get(self, request, *args, **kwargs):
        target_ideology = self.get_object()
        return self.process_affinity_request(
            target_object=target_ideology,
            target_key="target_ideology",
            target_value=target_ideology,
            explicit_value=True,
        )


@extend_schema(
    tags=["answers"],
    summary=_("Calculate affinity with a Completed Answer"),
    description=_(
        "Calculates the ideological affinity (0-100%) between a source (Authenticated User or CompletedAnswer UUID) "
        "and a target CompletedAnswer."
    ),
    parameters=[
        OpenApiParameter(
            name="source_answer_uuid",
            description=_("UUID of the source CompletedAnswer (required if anonymous)"),
            required=False,
            type=str,
            location=OpenApiParameter.QUERY,
        ),
        OpenApiParameter(
            name="target_answer_uuid",
            location=OpenApiParameter.PATH,
            description="UUID of the target CompletedAnswer",
            required=True,
            type=str,
        ),
    ],
    responses={200: AffinitySerializer},
)
class CompletedAnswerAffinityView(BaseAffinityView):
    serializer_class = AffinitySerializer
    queryset = CompletedAnswer.objects.all()
    lookup_field = "uuid"
    lookup_url_kwarg = "target_answer_uuid"

    def get(self, request, *args, **kwargs):
        target_answer = self.get_object()
        return self.process_affinity_request(
            target_object=target_answer,
            target_key="target_user",
            target_value=target_answer.completed_by,
            explicit_value=True,
        )

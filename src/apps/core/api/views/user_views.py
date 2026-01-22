from core.api.permissions import IsVerified
from core.api.serializers import (
    AffinitySerializer,
    MeSerializer,
    UserSetPasswordSerializer,
)
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from ideology.models import (
    CompletedAnswer,
    IdeologyAbstractionComplexity,
    IdeologyAxis,
    IdeologySection,
)
from rest_framework import status
from rest_framework.generics import GenericAPIView, RetrieveUpdateAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


@extend_schema(
    tags=["users"],
    summary=_("Get or update current profile"),
    description=_(
        "Retrieve the profile information of the currently authenticated user "
        "or update their details."
    ),
)
class MeDetailView(RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MeSerializer

    def get_object(self):
        return self.request.user


@extend_schema(
    tags=["users"],
    summary=_("Set user password"),
    description=_(
        "Allows an authenticated user (e.g., logged in via Google) to set a password "
        "so they can use standard login in the future."
    ),
    responses={200: MeSerializer},
)
class UserSetPasswordView(UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSetPasswordSerializer

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save()

        return Response(MeSerializer(user).data, status=status.HTTP_200_OK)


@extend_schema(
    tags=["users"],
    summary=_("Get affinity with a Completed Answer"),
    description=_(
        "Calculates the ideological affinity (0-100%) between the current user's active answers "
        "and a specific CompletedAnswer (identified by UUID). The target might be anonymous."
    ),
)
class UserAffinityView(GenericAPIView):
    permission_classes = [IsAuthenticated, IsVerified]
    queryset = CompletedAnswer.objects.all()
    lookup_field = "uuid"
    serializer_class = AffinitySerializer

    def get(self, request, *args, **kwargs):
        target_answer = self.get_object()

        target_data_mapped = target_answer.get_mapped_for_calculation()

        affinity_data = request.user.get_affinity_data(target_data_mapped)

        comp_uuids = set()
        sec_uuids = set()
        axis_uuids = set()

        for comp in affinity_data["complexities"]:
            comp_uuids.add(comp["complexity_uuid"])
            for sec in comp["sections"]:
                sec_uuids.add(sec["section_uuid"])
                for ax in sec["axes"]:
                    axis_uuids.add(ax["axis_uuid"])

        comps_map = {
            c.uuid.hex: c
            for c in IdeologyAbstractionComplexity.objects.filter(uuid__in=comp_uuids)
        }
        secs_map = {
            s.uuid.hex: s for s in IdeologySection.objects.filter(uuid__in=sec_uuids)
        }
        axes_map = {
            ax.uuid.hex: ax for ax in IdeologyAxis.objects.filter(uuid__in=axis_uuids)
        }

        for comp_item in affinity_data["complexities"]:
            comp_item["complexity"] = comps_map.get(comp_item["complexity_uuid"])

            for section_item in comp_item["sections"]:
                section_item["section"] = secs_map.get(section_item["section_uuid"])

                for axis_item in section_item["axes"]:
                    axis_item["axis"] = axes_map.get(axis_item["axis_uuid"])

        response_data = {
            "target_user": target_answer.completed_by,
            "total": affinity_data["total"],
            "complexities": affinity_data["complexities"],
        }

        serializer = self.get_serializer(response_data)
        return Response(serializer.data, status=status.HTTP_200_OK)

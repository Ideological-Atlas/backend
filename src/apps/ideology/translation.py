from modeltranslation.translator import TranslationOptions, register

from .models import (
    Ideology,
    IdeologyAbstractionComplexity,
    IdeologyAxis,
    IdeologyConditioner,
    IdeologyReference,
    IdeologySection,
    Religion,
    Tag,
)


@register(Ideology)
class IdeologyTranslationOptions(TranslationOptions):
    fields = ("description_supporter", "description_detractor", "description_neutral")


@register(IdeologySection)
class IdeologySectionTranslationOptions(TranslationOptions):
    fields = ("name", "description", "condition_values")


@register(IdeologyAxis)
class IdeologyAxisTranslationOptions(TranslationOptions):
    fields = ("name", "description", "left_label", "right_label", "condition_values")


@register(IdeologyConditioner)
class IdeologyConditionerTranslationOptions(TranslationOptions):
    fields = ("name", "description", "accepted_values")


@register(IdeologyAbstractionComplexity)
class IdeologyAbstractionComplexityTranslationOptions(TranslationOptions):
    fields = ("name", "description")


@register(Religion)
class ReligionTranslationOptions(TranslationOptions):
    fields = ("name", "description")


@register(Tag)
class TagTranslationOptions(TranslationOptions):
    fields = ("name", "description")


@register(IdeologyReference)
class IdeologyReferenceTranslationOptions(TranslationOptions):
    fields = ("description",)

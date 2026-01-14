import uuid

import django.core.validators
import django.db.models.deletion
import django.utils.timezone
import model_utils.fields
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("ideology", "0002_remove_axisanswer_axis_answer_lower_bound_check_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]
    operations = [
        migrations.CreateModel(
            name="IdeologyAxisDefinition",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created",
                    model_utils.fields.AutoCreatedField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name="created",
                    ),
                ),
                (
                    "modified",
                    model_utils.fields.AutoLastModifiedField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name="modified",
                    ),
                ),
                (
                    "uuid",
                    models.UUIDField(
                        db_index=True, default=uuid.uuid4, editable=False, unique=True
                    ),
                ),
                (
                    "is_indifferent",
                    models.BooleanField(
                        default=False,
                        help_text="If true, the value is irrelevant/indifferent.",
                        verbose_name="Is Indifferent",
                    ),
                ),
                (
                    "value",
                    models.IntegerField(
                        blank=True,
                        null=True,
                        validators=[
                            django.core.validators.MinValueValidator(-100),
                            django.core.validators.MaxValueValidator(100),
                        ],
                        verbose_name="Position Value",
                    ),
                ),
                (
                    "margin_left",
                    models.IntegerField(
                        blank=True,
                        default=0,
                        null=True,
                        validators=[
                            django.core.validators.MinValueValidator(0),
                            django.core.validators.MaxValueValidator(200),
                        ],
                        verbose_name="Left Margin Tolerance",
                    ),
                ),
                (
                    "margin_right",
                    models.IntegerField(
                        blank=True,
                        default=0,
                        null=True,
                        validators=[
                            django.core.validators.MinValueValidator(0),
                            django.core.validators.MaxValueValidator(200),
                        ],
                        verbose_name="Right Margin Tolerance",
                    ),
                ),
            ],
            options={
                "verbose_name": "Ideology Axis Definition",
                "verbose_name_plural": "Ideology Axis Definitions",
            },
        ),
        migrations.CreateModel(
            name="IdeologyConditionerDefinition",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created",
                    model_utils.fields.AutoCreatedField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name="created",
                    ),
                ),
                (
                    "modified",
                    model_utils.fields.AutoLastModifiedField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name="modified",
                    ),
                ),
                (
                    "uuid",
                    models.UUIDField(
                        db_index=True, default=uuid.uuid4, editable=False, unique=True
                    ),
                ),
                ("answer", models.CharField(max_length=255, verbose_name="Answer")),
            ],
            options={
                "verbose_name": "Ideology Conditioner Definition",
                "verbose_name_plural": "Ideology Conditioner Definitions",
            },
        ),
        migrations.CreateModel(
            name="UserAxisAnswer",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created",
                    model_utils.fields.AutoCreatedField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name="created",
                    ),
                ),
                (
                    "modified",
                    model_utils.fields.AutoLastModifiedField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name="modified",
                    ),
                ),
                (
                    "uuid",
                    models.UUIDField(
                        db_index=True, default=uuid.uuid4, editable=False, unique=True
                    ),
                ),
                (
                    "is_indifferent",
                    models.BooleanField(
                        default=False,
                        help_text="If true, the value is irrelevant/indifferent.",
                        verbose_name="Is Indifferent",
                    ),
                ),
                (
                    "value",
                    models.IntegerField(
                        blank=True,
                        null=True,
                        validators=[
                            django.core.validators.MinValueValidator(-100),
                            django.core.validators.MaxValueValidator(100),
                        ],
                        verbose_name="Position Value",
                    ),
                ),
                (
                    "margin_left",
                    models.IntegerField(
                        blank=True,
                        default=0,
                        null=True,
                        validators=[
                            django.core.validators.MinValueValidator(0),
                            django.core.validators.MaxValueValidator(200),
                        ],
                        verbose_name="Left Margin Tolerance",
                    ),
                ),
                (
                    "margin_right",
                    models.IntegerField(
                        blank=True,
                        default=0,
                        null=True,
                        validators=[
                            django.core.validators.MinValueValidator(0),
                            django.core.validators.MaxValueValidator(200),
                        ],
                        verbose_name="Right Margin Tolerance",
                    ),
                ),
            ],
            options={
                "verbose_name": "User Axis Answer",
                "verbose_name_plural": "User Axis Answers",
            },
        ),
        migrations.CreateModel(
            name="UserConditionerAnswer",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created",
                    model_utils.fields.AutoCreatedField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name="created",
                    ),
                ),
                (
                    "modified",
                    model_utils.fields.AutoLastModifiedField(
                        default=django.utils.timezone.now,
                        editable=False,
                        verbose_name="modified",
                    ),
                ),
                (
                    "uuid",
                    models.UUIDField(
                        db_index=True, default=uuid.uuid4, editable=False, unique=True
                    ),
                ),
                ("answer", models.CharField(max_length=255, verbose_name="Answer")),
            ],
            options={
                "verbose_name": "User Conditioner Answer",
                "verbose_name_plural": "User Conditioner Answers",
            },
        ),
        migrations.RemoveConstraint(
            model_name="axisanswer",
            name="unique_ideology_axis_position",
        ),
        migrations.RemoveConstraint(
            model_name="axisanswer",
            name="unique_user_axis_result",
        ),
        migrations.RemoveConstraint(
            model_name="axisanswer",
            name="axis_answer_owner_xor_constraint",
        ),
        migrations.RemoveConstraint(
            model_name="axisanswer",
            name="axis_answer_lower_bound_check",
        ),
        migrations.RemoveConstraint(
            model_name="axisanswer",
            name="axis_answer_upper_bound_check",
        ),
        migrations.RemoveConstraint(
            model_name="conditioneranswer",
            name="unique_ideology_conditioner_answer",
        ),
        migrations.RemoveConstraint(
            model_name="conditioneranswer",
            name="unique_user_conditioner_answer",
        ),
        migrations.RemoveConstraint(
            model_name="conditioneranswer",
            name="conditioner_answer_owner_xor_constraint",
        ),
        migrations.AddField(
            model_name="ideologyaxisdefinition",
            name="axis",
            field=models.ForeignKey(
                help_text="The specific axis being measured.",
                on_delete=django.db.models.deletion.CASCADE,
                to="ideology.ideologyaxis",
                verbose_name="Axis",
            ),
        ),
        migrations.AddField(
            model_name="ideologyaxisdefinition",
            name="ideology",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="axis_definitions",
                to="ideology.ideology",
                verbose_name="Ideology",
            ),
        ),
        migrations.AddField(
            model_name="ideologyconditionerdefinition",
            name="conditioner",
            field=models.ForeignKey(
                help_text="The question or variable being answered.",
                on_delete=django.db.models.deletion.CASCADE,
                to="ideology.ideologyconditioner",
                verbose_name="Conditioner",
            ),
        ),
        migrations.AddField(
            model_name="ideologyconditionerdefinition",
            name="ideology",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="conditioner_definitions",
                to="ideology.ideology",
                verbose_name="Ideology",
            ),
        ),
        migrations.AddField(
            model_name="useraxisanswer",
            name="axis",
            field=models.ForeignKey(
                help_text="The specific axis being measured.",
                on_delete=django.db.models.deletion.CASCADE,
                to="ideology.ideologyaxis",
                verbose_name="Axis",
            ),
        ),
        migrations.AddField(
            model_name="useraxisanswer",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="axis_answers",
                to=settings.AUTH_USER_MODEL,
                verbose_name="User",
            ),
        ),
        migrations.AddField(
            model_name="userconditioneranswer",
            name="conditioner",
            field=models.ForeignKey(
                help_text="The question or variable being answered.",
                on_delete=django.db.models.deletion.CASCADE,
                to="ideology.ideologyconditioner",
                verbose_name="Conditioner",
            ),
        ),
        migrations.AddField(
            model_name="userconditioneranswer",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="conditioner_answers",
                to=settings.AUTH_USER_MODEL,
                verbose_name="User",
            ),
        ),
        migrations.RemoveField(
            model_name="conditioneranswer",
            name="conditioner",
        ),
        migrations.RemoveField(
            model_name="conditioneranswer",
            name="ideology",
        ),
        migrations.RemoveField(
            model_name="conditioneranswer",
            name="user",
        ),
        migrations.AlterUniqueTogether(
            name="ideologyaxisdefinition",
            unique_together={("ideology", "axis")},
        ),
        migrations.AlterUniqueTogether(
            name="ideologyconditionerdefinition",
            unique_together={("ideology", "conditioner")},
        ),
        migrations.AlterUniqueTogether(
            name="useraxisanswer",
            unique_together={("user", "axis")},
        ),
        migrations.AlterUniqueTogether(
            name="userconditioneranswer",
            unique_together={("user", "conditioner")},
        ),
        migrations.DeleteModel(
            name="AxisAnswer",
        ),
        migrations.DeleteModel(
            name="ConditionerAnswer",
        ),
    ]

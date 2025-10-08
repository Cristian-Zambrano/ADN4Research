from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.db import transaction

from design.models import (
	Framework,
	Researcher,
	ResearchQuestion,
	ResearchOwner,
	ApprovalCenter,
	ApprovalItem,
)
from design.services.services import ResearchQuestionSubmissionService
from design.dto.dto import SubmitDraftForReviewCommand


def _ensure_demo_frameworks():
	# Ensure the three common frameworks exist for the demo
	Framework.objects.get_or_create(
		name="PEO",
		defaults={
			"fields": {"Population": "", "Exposure": "", "Outcome": ""},
		},
	)
	Framework.objects.get_or_create(
		name="PICO",
		defaults={
			"fields": {
				"Population": "",
				"Intervention": "",
				"Comparison": "",
				"Outcome": "",
			},
		},
	)
	Framework.objects.get_or_create(
		name="PCC",
		defaults={
			"fields": {"Population": "", "Concept": "", "Context": ""},
		},
	)


def _get_or_create_demo_researcher():
	user, _ = User.objects.get_or_create(
		username="demo_researcher", defaults={"is_active": True}
	)
	researcher, _ = Researcher.objects.get_or_create(
		user=user, defaults={"name": "Demo Researcher"}
	)
	return researcher


def _ensure_demo_owner():
	user, _ = User.objects.get_or_create(
		username="demo_owner", defaults={"is_active": True}
	)
	owner, _ = ResearchOwner.objects.get_or_create(
		user=user, defaults={"name": "Demo Owner"}
	)
	ApprovalCenter.objects.get_or_create(owner=owner)
	return owner


@transaction.atomic
def submit_reformulation(request):
	"""Simple form to submit a reformulated question for review."""
	_ensure_demo_frameworks()

	frameworks = Framework.objects.all().order_by("name")
	selected_framework_id = request.GET.get("framework") or request.POST.get(
		"framework_id"
	)
	selected_framework = (
		Framework.objects.filter(id=selected_framework_id).first()
		if selected_framework_id
		else None
	)
	field_keys = list(selected_framework.fields.keys()) if selected_framework else []

	if request.method == "POST":
		researcher = _get_or_create_demo_researcher()
		_ensure_demo_owner()  # ensure owner/inbox exists for demo

		original_text = (request.POST.get("original_text") or "").strip()
		reformulated_text = (request.POST.get("reformulated_text") or "").strip()
		filled_fields = {k: (request.POST.get(f"field_{k}") or "").strip() for k in field_keys}

		if not (
			selected_framework
			and original_text
			and reformulated_text
			and all(filled_fields.values())
		):
			messages.error(request, "Complete todos los campos.")
			return render(
				request,
				"design/submit_draft.html",
				{
					"frameworks": frameworks,
					"selected_framework": selected_framework,
					"field_keys": field_keys,
					"filled_fields": filled_fields,
					"original_text": original_text,
					"reformulated_text": reformulated_text,
				},
			)

		rq = ResearchQuestion.objects.create(
			original_text=original_text, created_by=researcher
		)
		cmd = SubmitDraftForReviewCommand(
			researcher_id=researcher.id,
			research_question_id=rq.id,
			framework_id=selected_framework.id,
			filled_fields=filled_fields,
			reformulated_text=reformulated_text,
			status="to_review",
		)
		result = ResearchQuestionSubmissionService().submit_draft_for_review(cmd)
		messages.success(
			request,
			"Borrador enviado para revisión." if result == 1 else "Borrador guardado en historial.",
		)
		return redirect("design_owner_inbox")

	return render(
		request,
		"design/submit_draft.html",
		{
			"frameworks": frameworks,
			"selected_framework": selected_framework,
			"field_keys": field_keys,
		},
	)


def owner_inbox(request):
	owner = _ensure_demo_owner()
	center = owner.approval_center
	items = (
		ApprovalItem.objects.filter(approval_center=center)
		.select_related(
			"iteration",
			"iteration__research_question",
			"iteration__researcher",
		)
		.order_by("-submitted_at")
	)
	return render(
		request,
		"design/owner_inbox.html",
		{
			"owner": owner,
			"items": items,
		},
	)

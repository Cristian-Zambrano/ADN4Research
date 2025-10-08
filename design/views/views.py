from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponseBadRequest
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
	ReformulatedResearchQuestionIteration,
)
from design.services.services import ResearchQuestionSubmissionService
from design.dto.dto import SubmitDraftForReviewCommand, AutosaveDraftCommand


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
	iter_id = request.GET.get("iter_id") or request.POST.get("iter_id")
	selected_framework_id = request.GET.get("framework") or request.POST.get("framework_id")
	selected_framework = Framework.objects.filter(id=selected_framework_id).first() if selected_framework_id else None

	# Defaults for form fields
	original_text = ""
	reformulated_text = ""
	filled_fields = {}

	# If continuing from an existing incomplete iteration, prefill the form
	if iter_id:
		try:
			existing = ApprovalItem.objects.none()  # placeholder to keep select_related import used
			iteration = ReformulatedResearchQuestionIteration.objects.select_related("research_question", "framework").get(id=iter_id)
			selected_framework = selected_framework or iteration.framework
			selected_framework_id = selected_framework.id if selected_framework else None
			original_text = iteration.research_question.original_text
			reformulated_text = iteration.reformulated_research_question or ""
			filled_fields = dict(iteration.filled_fields or {})
		except ReformulatedResearchQuestionIteration.DoesNotExist:
			pass

	field_keys = list(selected_framework.fields.keys()) if selected_framework else []
	field_rows = [{"name": k, "value": filled_fields.get(k, "")} for k in field_keys]

	if request.method == "POST":
		researcher = _get_or_create_demo_researcher()
		_ensure_demo_owner()  # ensure owner/inbox exists for demo

		original_text = (request.POST.get("original_text") or original_text).strip()
		reformulated_text = (request.POST.get("reformulated_text") or reformulated_text).strip()
		filled_fields = {k: (request.POST.get(f"field_{k}") or "").strip() for k in field_keys}

		# Ensure we have a ResearchQuestion to attach iterations
		rq = None
		if iter_id:
			try:
				iteration = ReformulatedResearchQuestionIteration.objects.select_related("research_question").get(id=iter_id)
				rq = iteration.research_question
			except ReformulatedResearchQuestionIteration.DoesNotExist:
				rq = None
		if rq is None:
			if not (selected_framework and original_text):
				messages.error(request, "Seleccione un framework y escriba la pregunta original para continuar.")
				return render(
					request,
					"design/submit_draft.html",
					{
						"frameworks": frameworks,
						"selected_framework": selected_framework,
						"field_rows": field_rows,
						"field_keys": field_keys,
						"original_text": original_text,
						"reformulated_text": reformulated_text,
						"iter_id": iter_id or "",
					},
				)
			rq = ResearchQuestion.objects.create(original_text=original_text, created_by=researcher)

		service = ResearchQuestionSubmissionService()
		# Require complete inputs for submission
		if not (
			selected_framework and original_text and reformulated_text and all(filled_fields.values())
		):
			messages.error(request, "Complete todos los campos para enviar a revisión. El borrador se guarda automáticamente.")
			return render(
				request,
				"design/submit_draft.html",
				{
					"frameworks": frameworks,
					"selected_framework": selected_framework,
					"field_rows": [{"name": k, "value": filled_fields.get(k, "")} for k in field_keys],
					"field_keys": field_keys,
					"original_text": original_text,
					"reformulated_text": reformulated_text,
					"iter_id": iter_id or "",
				},
			)
		cmd = SubmitDraftForReviewCommand(
			researcher_id=researcher.id,
			research_question_id=rq.id,
			framework_id=selected_framework.id,
			filled_fields=filled_fields,
			reformulated_text=reformulated_text,
			status="to_review",
		)
		result = service.submit_draft_for_review(cmd)
		messages.success(request, "Borrador enviado para revisión." if result == 1 else "Borrador guardado en historial.")
		return redirect("design_owner_inbox")

	return render(
		request,
		"design/submit_draft.html",
		{
			"frameworks": frameworks,
			"selected_framework": selected_framework,
			"field_rows": field_rows,
			"field_keys": field_keys,
			"original_text": original_text,
			"reformulated_text": reformulated_text,
			"iter_id": iter_id or "",
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


def researcher_history(request):
	researcher = _get_or_create_demo_researcher()
	iterations = (
		ReformulatedResearchQuestionIteration.objects
		.filter(researcher=researcher)
		.select_related("research_question", "framework")
		.order_by("-created_at")
	)
	return render(
		request,
		"design/history.html",
		{
			"researcher": researcher,
			"iterations": iterations,
		},
	)


@transaction.atomic
def autosave_draft_api(request):
	if request.method != "POST":
		return HttpResponseBadRequest("Invalid method")

	researcher = _get_or_create_demo_researcher()

	iter_id = request.POST.get("iter_id")
	rq_id = request.POST.get("rq_id")
	framework_id = request.POST.get("framework_id")
	original_text = (request.POST.get("original_text") or "").strip()
	reformulated_text = (request.POST.get("reformulated_text") or "")

	# Build filled_fields from POST keys starting with field_
	filled_fields = {}
	for k, v in request.POST.items():
		if k.startswith("field_"):
			filled_fields[k.replace("field_", "", 1)] = (v or "").strip()

	# Resolve ResearchQuestion
	research_question = None
	if iter_id:
		try:
			iteration = ReformulatedResearchQuestionIteration.objects.select_related("research_question").get(id=iter_id)
			research_question = iteration.research_question
			rq_id = research_question.id
		except ReformulatedResearchQuestionIteration.DoesNotExist:
			pass
	if (not research_question) and rq_id:
		try:
			research_question = ResearchQuestion.objects.get(id=rq_id)
		except ResearchQuestion.DoesNotExist:
			research_question = None

	# Precondition to autosave: must have framework and original_text
	if not (framework_id and original_text):
		return JsonResponse({"ok": False, "reason": "missing_prereq"})

	# If no RQ yet, create it now for autosave
	if research_question is None:
		research_question = ResearchQuestion.objects.create(
			original_text=original_text,
			created_by=researcher,
		)

	service = ResearchQuestionSubmissionService()
	cmd = AutosaveDraftCommand(
		researcher_id=researcher.id,
		research_question_id=research_question.id,
		framework_id=int(framework_id),
		filled_fields=filled_fields,
		reformulated_text=reformulated_text,
	)
	draft = service.autosave_draft(cmd)

	return JsonResponse({
		"ok": True,
		"draft_id": draft.id,
		"rq_id": research_question.id,
		"status": draft.status,
	})

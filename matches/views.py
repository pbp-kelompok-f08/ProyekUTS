from django.db.models import Count, F, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_http_methods

from .forms import MatchForm, MatchSearchForm, ParticipationForm
from .models import Match, Participation, SportCategory


DEFAULT_CATEGORIES = [
    "Sepak Bola",
    "Basket",
    "Bulu Tangkis",
    "Futsal",
    "Lari",
    "Bersepeda",
]


def _ensure_default_categories() -> None:
    for name in DEFAULT_CATEGORIES:
        SportCategory.objects.get_or_create(name=name)


def _serialize_match(match: Match) -> dict:
    return {
        "id": match.id,
        "title": match.title,
        "category": match.category.name,
        "category_slug": match.category.slug,
        "location": match.location,
        "event_date": match.event_date.isoformat(),
        "description": match.description,
        "max_members": match.max_members,
        "current_members": match.current_members,
        "available_slots": match.available_slots,
    }


@require_http_methods(["GET"])
def match_dashboard(request):
    _ensure_default_categories()

    matches = (
        Match.objects.select_related("category")
        .annotate(participant_count=Count("participations"))
        .order_by("event_date")
    )

    search_form = MatchSearchForm(request.GET or None)
    if search_form.is_valid():
        category = search_form.cleaned_data.get("category")
        keyword = search_form.cleaned_data.get("keyword")
        available_only = search_form.cleaned_data.get("available_only")

        if category:
            matches = matches.filter(category=category)

        if keyword:
            matches = matches.filter(
                Q(title__icontains=keyword)
                | Q(description__icontains=keyword)
                | Q(location__icontains=keyword)
            )

        if available_only:
            matches = matches.filter(participant_count__lt=F("max_members"))
    else:
        search_form = MatchSearchForm()

    match_list = list(matches)
    categories = SportCategory.objects.all()
    grouped_matches = [
        (category, [m for m in match_list if m.category_id == category.id])
        for category in categories
    ]
    has_any_match = any(matches for _, matches in grouped_matches)

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        payload = []
        for category, items in grouped_matches:
            if not items:
                continue
            payload.append(
                {
                    "category": category.name,
                    "category_slug": category.slug,
                    "matches": [_serialize_match(match) for match in items],
                }
            )
        return JsonResponse({"groups": payload})

    context = {
        "grouped_matches": grouped_matches,
        "match_form": MatchForm(),
        "participation_form": ParticipationForm(),
        "search_form": search_form,
        "has_any_match": has_any_match,
    }
    return render(request, "matches/dashboard.html", context)


@require_http_methods(["POST"])
def create_match(request):
    form = MatchForm(request.POST)
    if form.is_valid():
        match = form.save()
        return JsonResponse(
            {
                "success": True,
                "message": "Match baru berhasil dibuat.",
                "match": _serialize_match(match),
            },
            status=201,
        )

    return JsonResponse({"success": False, "errors": form.errors}, status=400)


@require_http_methods(["POST"])
def book_match(request, pk: int):
    match = get_object_or_404(Match.objects.select_related("category"), pk=pk)

    if match.available_slots <= 0:
        return JsonResponse(
            {
                "success": False,
                "errors": {
                    "__all__": ["Match ini sudah penuh. Pilih match lain atau buat baru."]
                },
            },
            status=400,
        )

    form = ParticipationForm(request.POST)
    if form.is_valid():
        participation: Participation = form.save(commit=False)
        participation.match = match
        participation.save()

        updated_match = Match.objects.select_related("category").get(pk=pk)

        return JsonResponse(
            {
                "success": True,
                "message": "Kamu berhasil mendaftar pada match ini.",
                "match": _serialize_match(updated_match),
            }
        )

    return JsonResponse({"success": False, "errors": form.errors}, status=400)

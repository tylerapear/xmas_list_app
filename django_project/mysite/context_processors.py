from xmas_lists.models import EventInvite

def pending_invites(request):
    if request.user.is_authenticated:
        pending_invites = EventInvite.objects.filter(
            user=request.user,
            accepted_at__isnull=True,
            rejected_at__isnull=True
        )
        return {'pending_invites': pending_invites}
    return {'pending_invites': []}
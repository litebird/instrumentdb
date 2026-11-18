# browse/signals.py

from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from browse.models import Release
from allauth.account.signals import email_confirmed


@receiver(m2m_changed, sender=Release.data_files.through)
def update_release_json_on_m2m(sender, instance, action, reverse, pk_set, **kwargs):
    """
    Triggers when data_files are added/removed/cleared from a Release.
    """
    if action in ["post_add", "post_remove", "post_clear"]:
        if reverse:
            # The change was triggered from the Release side (related_name).
            # instance is the Release object.
            instance.generate_json_dump()
        else:
            # The change was triggered from the DataFile side (where the field is defined).
            # instance is a DataFile. The affected Releases are in pk_set.
            if pk_set:
                for release_tag in pk_set:
                    release = Release.objects.get(pk=release_tag)
                    release.generate_json_dump()


@receiver(email_confirmed)
def deactivate_pending_user(request, email_address, **kwargs):
    user = email_address.user
    user.is_active = False
    user.save(update_fields=["is_active"])

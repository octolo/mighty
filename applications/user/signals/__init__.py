from django.apps import apps
from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

from mighty.applications.user import get_user_email_model, get_user_phone_model
from mighty.applications.user.apps import UserConfig

UserModel = get_user_model()
UserEmailModel = get_user_email_model()
UserPhoneModel = get_user_phone_model()

import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=UserModel)
def create_user_identifiers(sender, instance, created, **kwargs):
    if created and (instance.email or instance.phone):
        # If the user is created, create a primary email and/or phone
        with transaction.atomic():
            try:
                if instance.email:
                    logger.info(
                        f'create_user_identifiers: create primary email {instance.email}'
                    )
                    UserEmailModel.objects.create(
                        user=instance, email=instance.email, primary=True
                    )
                if instance.phone:
                    logger.info(
                        f'create_user_identifiers: create primary phone {instance.phone}'
                    )
                    UserPhoneModel.objects.create(
                        user=instance, phone=instance.phone, primary=True
                    )
            except Exception as e:
                logger.error(f'create_user_identifiants: {e}')


# This signal help us to monitor and find user based on their primary and verified email
# At the moment it does not imply any action
@receiver(post_delete, sender=UserEmailModel)
def SetPrimaryEmailAddressAfterDeleteEmail(sender, instance, **kwargs):
    user = instance.user

    # Check if the user has any primary email left
    if not UserEmailModel.objects.filter(
        user=user, **{UserConfig.ForeignKey.email_primary: True}
    ).exists():
        # Find the first verified email, or the first non-verified if none are verified
        email = (
            UserEmailModel.objects.filter(user=user)
            .order_by('-verified')
            .first()
        )

        with transaction.atomic():
            if email:
                logger.info(
                    f'SetPrimaryEmailAddressAfterDeleteEmail: set {email.email} as primary email'
                )
                if apps.is_installed('allauth'):
                    email.set_as_primary()
                else:
                    # FIXME: Temporary until other email models are removed, not used either way
                    setattr(email, UserConfig.ForeignKey.email_primary, True)
                    email.save()
            else:
                logger.info(
                    f'SetPrimaryEmailAddressAfterDeleteEmail: no email found, clear email field {user.email}'
                )
                # If no verified email is found, clear the email field
                user.email = None
                user.save()


@receiver(post_delete, sender=UserPhoneModel)
def SetPrimaryUserPhoneAfterDeletePhone(sender, instance, **kwargs):
    user = instance.user

    # Check if the user has any primary phone left
    if not UserPhoneModel.objects.filter(user=user, primary=True).exists():
        # Find the first verified phone, or the first non-verified if none are verified
        phone = (
            UserPhoneModel.objects.filter(user=user)
            .order_by('-verified')
            .first()
        )

        with transaction.atomic():
            if phone:
                logger.info(
                    f'SetPrimaryPhoneNumberAfterDeletePhone: set {phone.phone} as primary phone'
                )
                phone.set_as_primary()
            else:
                logger.info(
                    f'SetPrimaryPhoneNumberAfterDeletePhone: no phone found, clear phone field {user.phone}'
                )
                # If no verified phone is found, clear the phone field
                # Upodate user phone field
                UserModel.objects.filter(pk=user.pk).update(phone=None)


@receiver(post_save, sender=UserEmailModel)
def SetPrimaryUserEmailAfterSaveEmail(sender, instance, created, **kwargs):
    user = instance.user
    # Check if the user has any primary email left
    if not UserEmailModel.objects.filter(
        user=user, **{UserConfig.ForeignKey.email_primary: True}
    ).exists():
        # If the email is created and no other email exists, set it as primary
        if created and not user.email:
            with transaction.atomic():
                logger.info(
                    f'SetPrimaryUserEmailAfterSaveEmail: set {instance.email} as primary email'
                )
                instance.set_as_primary()
        else:
            # Find the first verified email, or the first non-verified if none are verified
            email = (
                UserEmailModel.objects.filter(user=user)
                .exclude(pk=instance.pk)
                .order_by('-verified')
                .first()
            )
            # If a email is found, set it as primary
            if email:
                logger.info(
                    f'SetPrimaryUserEmailAfterSaveEmail: set {email.email} as primary email'
                )
                email.set_as_primary()
            # if not email is found, set the current email as primary
            else:
                logger.info(
                    f'SetPrimaryUserEmailAfterSaveEmail: no other email found, force set {instance.email} as primary email'
                )
                # If no verified email is found, clear the email field
                instance.set_as_primary()


@receiver(post_save, sender=UserPhoneModel)
def SetPrimaryUserPhoneAfterSavePhone(sender, instance, created, **kwargs):
    user = instance.user
    # Check if the user has any primary phone left
    if not UserPhoneModel.objects.filter(user=user, primary=True).exists():
        # If the phone is created and no other phone exists, set it as primary
        if created and not user.phone:
            with transaction.atomic():
                logger.info(
                    f'SetPrimaryUserPhoneAfterSavePhone: set {instance.phone} as primary phone'
                )
                instance.set_as_primary()
        else:
            # Find the first verified phone, or the first non-verified if none are verified
            phone = (
                UserPhoneModel.objects.filter(user=user)
                .exclude(pk=instance.pk)
                .order_by('-verified')
                .first()
            )
            # If a phone is found, set it as primary
            if phone:
                logger.info(
                    f'SetPrimaryUserPhoneAfterSavePhone: set {phone.phone} as primary phone'
                )
                phone.set_as_primary()
            # if not phone is found, set the current phone as primary
            else:
                logger.info(
                    f'SetPrimaryUserPhoneAfterSavePhone: no other phone found, force set {instance.phone} as primary phone'
                )
                # If no verified phone is found, clear the phone field
                instance.set_as_primary()


@receiver(pre_save, sender=UserEmailModel)
def handleFormSetAsPrimaryEmail(sender, instance, **kwargs):
    if instance.primary:
        # Remove primary from other emails
        UserEmailModel.objects.filter(user=instance.user).exclude(
            pk=instance.pk
        ).update(primary=False)

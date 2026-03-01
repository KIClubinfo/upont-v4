import base64
import os

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from django.contrib.auth.decorators import login_required
from django.contrib.postgres.search import TrigramSimilarity
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Q
from django.db.models.functions import Greatest
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from .forms import AddMember, AddRole, ClubRequestForm, EditClub, EditProfile
from .models import (
    Category,
    Channel,
    ChannelEncryptedKey,
    ChannelJoinRequest,
    Club,
    Membership,
    Message,
    NotificationToken,
    Promotion,
    Role,
    Student,
)
from .serializers import (
    ClubSerializer,
    ClubSerializerLite,
    RoleSerializer,
    StudentSerializer,
)


@login_required
def index_users(request):
    all_student_list = Student.objects.order_by(
        "-promo__year", "user__first_name", "user__last_name"
    )
    context = {
        "all_student_list": all_student_list,
        "display_students_with_react": True,
    }
    return render(request, "social/index_users.html", context)


class StudentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows students to be viewed.
    """

    queryset = Student.objects.all().order_by(
        "-promo__year", "user__first_name", "user__last_name"
    )
    serializer_class = StudentSerializer

    @action(url_path="profile/update", detail=False, methods=["post"])
    def update_profile(self, request, *args, **kwargs):
        print("mskdf")
        student = get_object_or_404(Student, user__id=request.user.id)
        form = EditProfile(request.data, instance=student)
        print(request.data)
        if form.is_valid():
            if "promo" in request.data:
                try:
                    promotion = Promotion.objects.get(nickname=request.data["promo"])
                    student.promo = promotion
                    student.save()
                except Promotion.DoesNotExist:
                    return Response(
                        {
                            "status": "error",
                            "errors": {"promotion": ["Promotion invalide !"]},
                        }
                    )
            if "picture" in request.data:
                student.picture.delete(save=False)
                student.picture = request.data["picture"]
                student.save()
            if "first_connection" in request.data:
                student.first_connection = request.data["first_connection"]
                student.save()
            form.save()
            return Response({"status": "ok"})
        else:
            print(form.errors)
            return Response({"status": "error", "errors": form.errors})

    @action(detail=False, methods=["get"])
    def unvalidated(self, request):
        """Returns list of unvalidated students"""
        if not (request.user.is_superuser or request.user.is_staff):
            return Response({"error": "Permission denied"}, status=403)

        unvalidated = Student.objects.filter(is_validated=False).order_by(
            "-promo__year", "user__first_name", "user__last_name"
        )
        serializer = StudentSerializer(unvalidated, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def birthdays_today(self, request):
        """Returns list of students whose birthday is today"""
        from datetime import datetime

        # Extract month and day from today's date
        today = datetime.now()

        # Filter students whose birthday matches today's month and day
        birthday_students = Student.objects.filter(
            birthdate__month=today.month, birthdate__day=today.day
        ).order_by("-promo__year", "user__first_name", "user__last_name")

        serializer = StudentSerializer(birthday_students, many=True)
        return Response(serializer.data)


class OneStudentView(APIView):
    """
    API endpoint that allows a unique student to be viewed.
    """

    def get(self, request):
        student = get_object_or_404(Student, user__id=request.GET["id"])
        serializer = StudentSerializer(student)
        return Response({"student": serializer.data})

    @classmethod
    def get_extra_actions(cls):
        return []


class CurrentStudentView(APIView):
    """
    API endpoint that returns the current student.
    """

    def get(self, request):
        student = get_object_or_404(Student, user__id=request.user.id)
        serializer = StudentSerializer(student)
        return Response({"student": serializer.data})

    @classmethod
    def get_extra_actions(cls):
        return []


class StudentCanPublishAs(APIView):
    """
    API endpoint that returns the clubs that student can publish as.
    """

    def get(self, request):
        data = {"-1": "Élève"}
        for membership in Membership.objects.filter(student__user__id=request.user.id):
            data[membership.club.id] = membership.club.name
        return Response({"can_publish_as": data})

    @classmethod
    def get_extra_actions(cls):
        return []


class StudentMembershipView(APIView):
    """
    API endpoint that returns the clubs that student can publish as.
    """

    def get(self, request):
        student = get_object_or_404(Student, user__pk=request.GET["id"])
        data = []
        for membership in Membership.objects.filter(student__user__id=student.user.id):
            club = Club.objects.get(id=membership.club.id)
            serializer = ClubSerializerLite(club)
            club_data = serializer.data
            club_data["is_admin"] = membership.is_admin
            club_data["is_old"] = membership.is_old
            club_data["role"] = membership.role.name
            data.append(club_data)
        return Response({"is_member_of": data})

    @classmethod
    def get_extra_actions(cls):
        return []


class SearchRole(APIView):
    """
    API endpoint that returns the roles whose name contains the query.
    """

    def get(self, request):
        if "role" in request.GET and request.GET["role"].strip():
            query = request.GET.get("role", None)
            roles = Role.objects.filter(name__icontains=query).order_by("-name")
        else:
            roles = Role.objects.all().order_by("-name")
        serializer = RoleSerializer(roles, many=True)
        return Response({"roles": serializer.data})


class SearchStudent(APIView):
    """
    API endpoint that returns the student whose username contains the query.
    """

    def get(self, request):
        if "user" in request.GET and request.GET["user"].strip():
            students, searched_expression = search_user(request)
            students = students[:25]
        else:
            students = Student.objects.all().order_by(
                "-promo__year", "user__first_name", "user__last_name"
            )[:25]
        serializer = StudentSerializer(students, many=True)
        return Response({"students": serializer.data})


class NotificationTokenView(APIView):
    """
    API endpoint that returns or edit the student whose username contains the query.
    """

    def post(self, request):
        token = request.data["token"]
        if not NotificationToken.objects.filter(token=token).exists():
            NotificationToken.objects.create(
                student=Student.objects.get(user__id=request.user.id), token=token
            )
            return Response({"status": "created"})
        return Response({"status": "exists"})


class ClubsViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows clubs to be viewed.
    """

    queryset = Club.objects.all().order_by("label", "name", "nickname")
    serializer_class = ClubSerializer
    http_method_names = ["get"]


class OneClubView(APIView):
    """
    API endpoint that allows a unique club to be viewed.
    """

    def get(self, request):
        club = get_object_or_404(Club, id=request.GET["id"])
        serializer = ClubSerializer(club)
        return Response({"club": serializer.data})

    @classmethod
    def get_extra_actions(cls):
        return []


class SearchClub(APIView):
    """
    API endpoint that returns the club whose name contains the query.
    """

    def get(self, request):
        if "club" in request.GET and request.GET["club"].strip():
            clubs, searched_expression = search_club(request)
            clubs = clubs[:25]
        else:
            clubs = Club.objects.all().order_by("label", "name", "nickname")[:25]
        serializer = ClubSerializer(clubs, many=True)
        return Response({"clubs": serializer.data})


class StudentProfileEdit(APIView):
    """
    API endpoint that allows a student to edit his profile.
    """

    def post(self, request, format=None):
        student = get_object_or_404(Student, user__id=request.user.id)

        form = EditProfile(request.data, instance=student)
        if form.is_valid():
            form.save()
            return Response({"status": "ok"})
        else:
            return Response({"status": "error", "errors": form.errors})


class ProfilePicUpdate(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, format=None):
        image = request.data["image"]
        print(request.data)
        student = get_object_or_404(Student, user__id=request.user.id)
        student.picture = image
        student.save()
        return Response({"status": "ok"})


class StudentPublicKeyView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        student = get_object_or_404(Student, user__id=request.user.id)
        return Response({"public_key": student.public_key})

    def post(self, request):
        public_key_pem = request.data.get("public_key", "")
        if not isinstance(public_key_pem, str) or not public_key_pem.strip():
            return Response(
                {"status": "error", "error": "La clé publique est requise."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            serialization.load_pem_public_key(
                public_key_pem.encode("utf-8"),
                backend=default_backend(),
            )
        except ValueError:
            return Response(
                {"status": "error", "error": "Format de clé publique invalide."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        student = get_object_or_404(Student, user__id=request.user.id)
        student.public_key = public_key_pem
        student.save(update_fields=["public_key"])
        return Response({"status": "ok"})


class ChannelListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        current_student = get_object_or_404(Student, user__id=request.user.id)
        scope = request.GET.get("scope", "mine")
        if scope == "all":
            channels = (
                Channel.objects.all()
                .select_related("creator__user", "club")
                .prefetch_related("members__user", "admins__user")
                .order_by("-date")
            )
        else:
            channels = (
                Channel.objects.filter(members=current_student)
                .select_related("creator__user", "club")
                .prefetch_related("members__user", "admins__user")
                .order_by("-date")
            )

        my_requests = {
            request.channel_id: request.status
            for request in ChannelJoinRequest.objects.filter(student=current_student)
        }

        payload = []
        for channel in channels:
            is_member = channel.members.filter(id=current_student.id).exists()
            is_admin = channel.admins.filter(id=current_student.id).exists()
            payload.append(
                {
                    "id": channel.id,
                    "name": channel.name,
                    "date": channel.date,
                    "creator_id": channel.creator.user.id if channel.creator else None,
                    "creator_username": (
                        channel.creator.user.username if channel.creator else None
                    ),
                    "club_id": channel.club.id if channel.club else None,
                    "club_name": channel.club.name if channel.club else None,
                    "members": [
                        {
                            "id": member.user.id,
                            "username": member.user.username,
                        }
                        for member in channel.members.all()
                    ],
                    "admins": [
                        {
                            "id": admin.user.id,
                            "username": admin.user.username,
                        }
                        for admin in channel.admins.all()
                    ],
                    "is_member": is_member,
                    "is_admin": is_admin,
                    "can_request_join": not is_member,
                    "join_request_status": my_requests.get(channel.id),
                    "has_encrypted_key": channel.encrypted_keys.filter(
                        student=current_student
                    ).exists(),
                }
            )

        return Response({"channels": payload})


class CreateChannel(APIView):
    """
    API endpoint that allows a student to create a channel
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        current_student = get_object_or_404(Student, user__id=request.user.id)
        member_ids = request.data.get("members", [])
        admin_ids = request.data.get("admins", [])
        channel_name = request.data.get("name", "").strip()

        if not channel_name:
            return Response(
                {"status": "error", "error": "Le nom du channel est requis."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not isinstance(member_ids, list) or not member_ids:
            return Response(
                {"status": "error", "error": "La liste des membres est invalide."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not isinstance(admin_ids, list):
            return Response(
                {"status": "error", "error": "La liste des admins est invalide."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if request.user.id not in member_ids:
            member_ids.append(request.user.id)
        if request.user.id not in admin_ids:
            admin_ids.append(request.user.id)

        members = list(Student.objects.filter(user__id__in=member_ids))
        if len(members) != len(set(member_ids)):
            return Response(
                {"status": "error", "error": "Certains membres sont introuvables."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        admins = list(Student.objects.filter(user__id__in=admin_ids))
        if len(admins) != len(set(admin_ids)):
            return Response(
                {"status": "error", "error": "Certains admins sont introuvables."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        member_student_ids = {student.id for student in members}
        if any(admin.id not in member_student_ids for admin in admins):
            return Response(
                {
                    "status": "error",
                    "error": "Tous les admins doivent faire partie des membres.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        channel_of = str(request.data.get("channel_of", "-1"))
        club = None
        if channel_of != "-1":
            club = get_object_or_404(Club, id=channel_of)
            is_admin_of_club = Membership.objects.filter(
                student=current_student,
                club=club,
                is_admin=True,
                is_old=False,
            ).exists()
            if not is_admin_of_club:
                return Response(
                    {
                        "status": "error",
                        "error": "Seuls les admins du club peuvent creer un channel de club.",
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )
            if Channel.objects.filter(club=club).exists():
                return Response(
                    {
                        "status": "error",
                        "error": "Un channel existe deja pour ce club.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # Validate and parse every member key before persisting anything.
        public_keys_by_student = {}
        for student in members:
            if not student.public_key:
                return Response(
                    {
                        "status": "error",
                        "error": (
                            "Tous les membres doivent avoir une clé publique "
                            f"(manquante pour {student.user.username})."
                        ),
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            try:
                public_keys_by_student[student.id] = serialization.load_pem_public_key(
                    student.public_key.encode("utf-8"),
                    backend=default_backend(),
                )
            except ValueError:
                return Response(
                    {
                        "status": "error",
                        "error": (
                            "La clé publique d'un membre est invalide "
                            f"({student.user.username})."
                        ),
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        with transaction.atomic():
            # Symmetric key to encrypt messages in the channel.
            key = os.urandom(32)
            encrypted_keys = []
            for student in members:
                encrypted_key = public_keys_by_student[student.id].encrypt(
                    key,
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None,
                    ),
                )
                encrypted_key_save = ChannelEncryptedKey.objects.create(
                    key=base64.b64encode(encrypted_key).decode("utf-8"),
                    student=student,
                )
                encrypted_keys.append(encrypted_key_save)

            channel = Channel.objects.create(
                name=channel_name,
                date=timezone.now(),
                creator=current_student,
                club=club,
            )
            channel.members.set(members)
            channel.admins.set(admins)
            channel.encrypted_keys.set(encrypted_keys)

        return Response(
            {"status": "ok", "channel_id": channel.id},
            status=status.HTTP_201_CREATED,
        )


class ChannelJoinRequestCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, channel_id):
        current_student = get_object_or_404(Student, user__id=request.user.id)
        channel = get_object_or_404(Channel, id=channel_id)

        if channel.members.filter(id=current_student.id).exists():
            return Response(
                {"status": "error", "error": "Vous etes deja membre de ce channel."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        join_request, created = ChannelJoinRequest.objects.get_or_create(
            channel=channel,
            student=current_student,
            defaults={"status": ChannelJoinRequest.Status.PENDING},
        )
        if not created and join_request.status == ChannelJoinRequest.Status.PENDING:
            return Response({"status": "exists"})
        if not created:
            join_request.status = ChannelJoinRequest.Status.PENDING
            join_request.save(update_fields=["status"])

        return Response({"status": "created"}, status=status.HTTP_201_CREATED)


class ChannelJoinRequestListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, channel_id):
        current_student = get_object_or_404(Student, user__id=request.user.id)
        channel = get_object_or_404(Channel, id=channel_id)

        if not channel.admins.filter(id=current_student.id).exists():
            return Response(
                {"status": "error", "error": "Seuls les admins du channel y ont accès."},
                status=status.HTTP_403_FORBIDDEN,
            )

        pending_requests = (
            ChannelJoinRequest.objects.filter(
                channel=channel,
                status=ChannelJoinRequest.Status.PENDING,
            )
            .select_related("student__user")
            .order_by("date")
        )

        return Response(
            {
                "requests": [
                    {
                        "id": join_request.id,
                        "channel_id": channel.id,
                        "student_id": join_request.student.user.id,
                        "student_username": join_request.student.user.username,
                        "student_first_name": join_request.student.user.first_name,
                        "student_last_name": join_request.student.user.last_name,
                        "student_full_name": (
                            f"{(join_request.student.user.first_name or '').strip()} "
                            f"{(join_request.student.user.last_name or '').strip()}"
                        ).strip()
                        or join_request.student.user.username,
                        "date": join_request.date,
                        "status": join_request.status,
                    }
                    for join_request in pending_requests
                ]
            }
        )


class ChannelJoinRequestAcceptView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, channel_id, join_request_id):
        current_student = get_object_or_404(Student, user__id=request.user.id)
        channel = get_object_or_404(Channel, id=channel_id)

        if not channel.admins.filter(id=current_student.id).exists():
            return Response(
                {"status": "error", "error": "Seuls les admins du channel y ont accès."},
                status=status.HTTP_403_FORBIDDEN,
            )

        join_request = get_object_or_404(
            ChannelJoinRequest,
            id=join_request_id,
            channel=channel,
        )
        if join_request.status != ChannelJoinRequest.Status.PENDING:
            return Response(
                {"status": "error", "error": "Cette demande n'est plus en attente."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        encrypted_key = request.data.get("encrypted_key")
        if not isinstance(encrypted_key, str) or not encrypted_key.strip():
            return Response(
                {"status": "error", "error": "encrypted_key est requis."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        encrypted_key = encrypted_key.strip()
        try:
            base64.b64decode(encrypted_key, validate=True)
        except Exception:
            return Response(
                {
                    "status": "error",
                    "error": "encrypted_key doit être une chaîne base64 valide.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            join_request.status = ChannelJoinRequest.Status.ACCEPTED
            join_request.save(update_fields=["status"])
            encrypted_key_obj = ChannelEncryptedKey.objects.create(
                key=encrypted_key,
                student=join_request.student,
            )
            channel.encrypted_keys.add(encrypted_key_obj)
            channel.members.add(join_request.student)

        return Response(
            {
                "status": "accepted",
                "channel_id": channel.id,
                "join_request_id": join_request.id,
                "student_id": join_request.student.user.id,
            }
        )


class StudentPublicKeyByUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        student = get_object_or_404(Student, user__id=user_id)
        if not student.public_key:
            return Response(
                {"status": "error", "error": "Cet utilisateur n'a pas de clé publique."},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response({"user_id": user_id, "public_key": student.public_key})


class ChannelAddMemberView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, channel_id):
        current_student = get_object_or_404(Student, user__id=request.user.id)
        channel = get_object_or_404(Channel, id=channel_id)

        if not channel.admins.filter(id=current_student.id).exists():
            return Response(
                {"status": "error", "error": "Seuls les admins du channel y ont accès."},
                status=status.HTTP_403_FORBIDDEN,
            )

        student_user_id = request.data.get("student_user_id")
        encrypted_key = request.data.get("encrypted_key")
        if student_user_id is None:
            return Response(
                {"status": "error", "error": "student_user_id est requis."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not isinstance(encrypted_key, str) or not encrypted_key.strip():
            return Response(
                {"status": "error", "error": "encrypted_key est requis."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            base64.b64decode(encrypted_key, validate=True)
        except (ValueError, TypeError):
            return Response(
                {
                    "status": "error",
                    "error": "encrypted_key doit être une chaîne base64 valide.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        student_to_add = get_object_or_404(Student, user__id=student_user_id)
        if channel.members.filter(id=student_to_add.id).exists():
            return Response(
                {"status": "error", "error": "Cet utilisateur est déjà membre du channel."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        with transaction.atomic():
            encrypted_key_obj = ChannelEncryptedKey.objects.create(
                key=encrypted_key,
                student=student_to_add,
            )
            channel.encrypted_keys.add(encrypted_key_obj)
            channel.members.add(student_to_add)
            ChannelJoinRequest.objects.filter(
                channel=channel,
                student=student_to_add,
                status=ChannelJoinRequest.Status.PENDING,
            ).update(status=ChannelJoinRequest.Status.ACCEPTED)

        return Response(
            {
                "status": "added",
                "channel_id": channel.id,
                "student_id": student_to_add.user.id,
            }
        )


class ChannelMembersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, channel_id):
        current_student = get_object_or_404(Student, user__id=request.user.id)
        channel = get_object_or_404(Channel, id=channel_id)

        if not channel.admins.filter(id=current_student.id).exists():
            return Response(
                {"status": "error", "error": "Seuls les admins du channel y ont accès."},
                status=status.HTTP_403_FORBIDDEN,
            )

        members = channel.members.select_related("user").all().order_by(
            "user__first_name", "user__last_name", "user__username"
        )
        admin_ids = set(channel.admins.values_list("id", flat=True))
        members_payload = []
        for member in members:
            first_name = (member.user.first_name or "").strip()
            last_name = (member.user.last_name or "").strip()
            full_name = f"{first_name} {last_name}".strip()
            members_payload.append(
                {
                    "student_id": member.id,
                    "user_id": member.user.id,
                    "username": member.user.username,
                    "full_name": full_name or member.user.username,
                    "is_admin": member.id in admin_ids,
                }
            )

        return Response({"channel_id": channel.id, "members": members_payload})


class ChannelRemoveMemberView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, channel_id, user_id):
        current_student = get_object_or_404(Student, user__id=request.user.id)
        channel = get_object_or_404(Channel, id=channel_id)

        if not channel.admins.filter(id=current_student.id).exists():
            return Response(
                {"status": "error", "error": "Seuls les admins du channel y ont accès."},
                status=status.HTTP_403_FORBIDDEN,
            )

        student_to_remove = get_object_or_404(Student, user__id=user_id)
        if not channel.members.filter(id=student_to_remove.id).exists():
            return Response(
                {"status": "error", "error": "Cet utilisateur n'est pas membre du channel."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        encrypted_keys_to_remove = list(
            channel.encrypted_keys.filter(student=student_to_remove)
        )
        with transaction.atomic():
            channel.members.remove(student_to_remove)
            channel.admins.remove(student_to_remove)
            if encrypted_keys_to_remove:
                channel.encrypted_keys.remove(*encrypted_keys_to_remove)
                ChannelEncryptedKey.objects.filter(
                    id__in=[key.id for key in encrypted_keys_to_remove]
                ).delete()

        return Response(
            {
                "status": "removed",
                "channel_id": channel.id,
                "student_id": student_to_remove.user.id,
            }
        )


class ChannelLeaveView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, channel_id):
        current_student = get_object_or_404(Student, user__id=request.user.id)
        channel = get_object_or_404(Channel, id=channel_id)

        if not channel.members.filter(id=current_student.id).exists():
            return Response(
                {"status": "error", "error": "Vous n'êtes pas membre de ce channel."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        encrypted_keys_to_remove = list(
            channel.encrypted_keys.filter(student=current_student)
        )
        with transaction.atomic():
            channel.members.remove(current_student)
            channel.admins.remove(current_student)
            if encrypted_keys_to_remove:
                channel.encrypted_keys.remove(*encrypted_keys_to_remove)
                ChannelEncryptedKey.objects.filter(
                    id__in=[key.id for key in encrypted_keys_to_remove]
                ).delete()

        return Response(
            {
                "status": "left",
                "channel_id": channel.id,
                "student_id": current_student.user.id,
            }
        )


class CreateMessage(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        current_student = get_object_or_404(Student, user__id=request.user.id)
        channel = get_object_or_404(Channel, id=request.data.get("channel"))

        if not channel.members.filter(id=current_student.id).exists():
            return Response(
                {"status": "error", "error": "Vous n'êtes pas membre de ce channel."},
                status=status.HTTP_403_FORBIDDEN,
            )

        content = request.data.get("content", "")
        if not content:
            return Response(
                {"status": "error", "error": "Le contenu du message est requis."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        by_club_value = str(request.data.get("by_club", "-1")).strip().lower()
        send_as_club = by_club_value in {"1", "true", "yes", "on"} or (
            by_club_value not in {"-1", "0", "false", "no", "off", ""}
        )

        club = None
        if send_as_club:
            if channel.club is None:
                return Response(
                    {
                        "status": "error",
                        "error": "Ce channel n'est pas un channel de club.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            club = channel.club
            can_publish_as_club = Membership.objects.filter(
                student=current_student,
                club=club,
                is_admin=True,
                is_old=False,
            ).exists()
            if not can_publish_as_club:
                return Response(
                    {
                        "status": "error",
                        "error": "Seuls les admins du club peuvent publier au nom du club.",
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

        message = Message.objects.create(
            channel=channel,
            date=timezone.now(),
            author=current_student,
            club=club,
            content=content,
        )
        return Response(
            {"status": "ok", "message_id": message.id},
            status=status.HTTP_201_CREATED,
        )


class ChannelMessagesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, channel_id):
        current_student = get_object_or_404(Student, user__id=request.user.id)
        channel = get_object_or_404(Channel, id=channel_id)

        if not channel.members.filter(id=current_student.id).exists():
            return Response(
                {"status": "error", "error": "Accès interdit à ce channel."},
                status=status.HTTP_403_FORBIDDEN,
            )

        messages = (
            Message.objects.filter(channel=channel)
            .select_related("author__user", "club")
            .order_by("date")
        )

        serialized_messages = []
        for message in messages:
            author_id = None
            author_username = None
            author_name = None
            if message.author:
                author_id = message.author.user.id
                author_username = message.author.user.username
                first_name = (message.author.user.first_name or "").strip()
                last_name = (message.author.user.last_name or "").strip()
                full_name = f"{first_name} {last_name}".strip()
                author_name = full_name or author_username
            serialized_messages.append(
                {
                    "id": message.id,
                    "channel": channel.id,
                    "date": message.date,
                    "author_id": author_id,
                    "author_username": author_username,
                    "author_name": author_name,
                    "club_id": message.club.id if message.club else None,
                    "club_name": message.club.name if message.club else None,
                    "content": message.content,
                }
            )

        return Response({"messages": serialized_messages})


class ChannelEncryptedKeyView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, channel_id):
        current_student = get_object_or_404(Student, user__id=request.user.id)
        channel = get_object_or_404(Channel, id=channel_id)

        if not channel.members.filter(id=current_student.id).exists():
            return Response(
                {"status": "error", "error": "Accès interdit à ce channel."},
                status=status.HTTP_403_FORBIDDEN,
            )

        encrypted_key = channel.encrypted_keys.filter(student=current_student).first()
        if encrypted_key is None:
            return Response(
                {"status": "error", "error": "Aucune clé chiffrée pour cet utilisateur."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            {
                "channel_id": channel.id,
                "student_id": current_student.id,
                "encrypted_key": encrypted_key.key,
            }
        )


class DeleteChannelView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, channel_id):
        current_student = get_object_or_404(Student, user__id=request.user.id)
        channel = get_object_or_404(Channel, id=channel_id)

        if not channel.admins.filter(id=current_student.id).exists():
            return Response(
                {"status": "error", "error": "Seuls les admins du channel peuvent le supprimer."},
                status=status.HTTP_403_FORBIDDEN,
            )

        encrypted_key_ids = list(channel.encrypted_keys.values_list("id", flat=True))
        with transaction.atomic():
            Message.objects.filter(channel=channel).delete()
            channel.encrypted_keys.clear()
            if encrypted_key_ids:
                ChannelEncryptedKey.objects.filter(id__in=encrypted_key_ids).delete()
            channel.delete()

        return Response({"status": "deleted", "channel_id": channel_id})


class DeleteChannelMessageView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, message_id):
        current_student = get_object_or_404(Student, user__id=request.user.id)
        message = get_object_or_404(Message.objects.select_related("channel", "author"), id=message_id)

        is_author = message.author_id == current_student.id
        is_channel_admin = bool(
            message.channel and message.channel.admins.filter(id=current_student.id).exists()
        )
        if not (is_author or is_channel_admin):
            return Response(
                {
                    "status": "error",
                    "error": "Seul l'auteur du message ou un admin du channel peut le supprimer.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        deleted_message_id = message.id
        message.delete()
        return Response({"status": "deleted", "message_id": deleted_message_id})


class DeleteAllChannelMessagesView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, channel_id):
        current_student = get_object_or_404(Student, user__id=request.user.id)
        channel = get_object_or_404(Channel, id=channel_id)

        if not channel.admins.filter(id=current_student.id).exists():
            return Response(
                {
                    "status": "error",
                    "error": "Seuls les admins du channel peuvent supprimer tous les messages.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        deleted_count, _ = Message.objects.filter(channel=channel).delete()
        return Response(
            {
                "status": "deleted",
                "channel_id": channel.id,
                "deleted_messages_count": deleted_count,
            }
        )


""" class ViewMessage(APIView):

 """


@login_required
def profile(request, user_id=None):
    if user_id is None:
        user_id = request.user.id
    student = get_object_or_404(Student, user__pk=user_id)
    membership_club_list = Membership.objects.filter(student__user__pk=user_id)
    all_student_list = Student.objects.order_by("user__first_name")
    context = {
        "all_student_list": all_student_list,
        "student": student,
        "membership_club_list": membership_club_list,
        "complete_name": student.user.first_name + " " + student.user.last_name,
    }
    if user_id == request.user.id:
        return render(request, "social/profile.html", context)
    else:
        return render(request, "social/profile_viewed.html", context)


@login_required
def search(request):
    searched_expression = "Si trouver quelque chose tu veux, le chercher il te faut."

    if "user" in request.GET:
        all_student_list = Student.objects.order_by("-promo__year", "user__first_name")
        context = {"all_student_list": all_student_list}
        if request.GET["user"].strip():
            found_students, searched_expression = search_user(request)
            context["student_displayed_list"] = found_students
        context["searched_expression"] = searched_expression
        return render(request, "social/index_users.html", context)

    if "club" in request.GET:
        all_clubs_list = Club.objects.order_by("name")
        all_categories_list = Category.objects.order_by("name")
        all_label_list = Club.Label.choices
        my_memberships_list = Membership.objects.filter(
            student__user__id=request.user.id
        )
        context = {
            "all_clubs_list": all_clubs_list,
            "all_categories_list": all_categories_list,
            "my_memberships_list": my_memberships_list,
            "all_label_list": all_label_list,
        }
        if request.GET["club"].strip():
            found_clubs, searched_expression = search_club(request)
            context["club_displayed_list"] = found_clubs
            context["asso_club_list"] = found_clubs.filter(label=Club.Label.ASSO)
            context["club_club_list"] = found_clubs.filter(label=Club.Label.CLUB)
            context["liste_club_list"] = found_clubs.filter(label=Club.Label.LISTE)
        context["searched_expression"] = searched_expression
        return render(request, "social/index_clubs.html", context)

    raise Http404


def partition(words):
    gaps = len(words) - 1  # one gap less than words (fencepost problem)
    for i in range(1, 1 << gaps):  # the 2^n possible partitions
        result = words[:1]  # The result starts with the first word
        for word in words[1:]:
            if i & 1:
                result.append(word)  # If "1" split at the gap
            else:
                result[-1] += " " + word  # If "0", don't split at the gap
            i >>= 1  # Next 0 or 1 indicating split or don't split
        yield result  # cough up r


def search_user(request):
    searched_expression = request.GET.get("user", None)
    key_words_list = [word.strip() for word in searched_expression.split()]
    all_possible_lists = [key_words_list]
    if len(key_words_list) > 1:
        all_possible_lists += [
            possible_list for possible_list in partition(key_words_list)
        ]
    queryset = Student.objects.none()

    for possible_list in all_possible_lists:
        partial_queryset = Student.objects.all()

        for key_word in possible_list:
            partial_queryset = partial_queryset.annotate(
                similarity=Greatest(
                    TrigramSimilarity("user__first_name", key_word),
                    TrigramSimilarity("user__last_name", key_word),
                    TrigramSimilarity("promo__nickname", key_word),
                    TrigramSimilarity("department", key_word),
                )
            )
            partial_queryset = partial_queryset.filter(
                Q(user__first_name__trigram_similar=key_word)
                | Q(user__last_name__trigram_similar=key_word)
                | Q(promo__nickname__iexact=key_word)
                | Q(department__iexact=key_word),
                similarity__gt=0.3,
            )
        queryset |= partial_queryset
    found_students = queryset.order_by("-promo__year", "user__first_name")
    return found_students, searched_expression


def search_club(request):
    searched_expression = request.GET.get("club", None)
    key_words_list = [word.strip() for word in searched_expression.split()]
    all_possible_lists = [key_words_list]
    if len(key_words_list) > 1:
        all_possible_lists += [
            possible_list for possible_list in partition(key_words_list)
        ]

    queryset = Club.objects.none()

    for possible_list in all_possible_lists:
        partial_queryset = Club.objects.all()

        for key_word in possible_list:
            partial_queryset = partial_queryset.annotate(
                similarity=Greatest(
                    TrigramSimilarity("name", key_word),
                    TrigramSimilarity("nickname", key_word),
                    TrigramSimilarity("category__name", key_word),
                )
            )
            partial_queryset = partial_queryset.filter(
                Q(name__trigram_similar=key_word)
                | Q(nickname__iexact=key_word)
                | Q(category__name__iexact=key_word)
                | Q(label__iexact=key_word),
                similarity__gt=0.3,
            )
        queryset |= partial_queryset.distinct("name")
    found_clubs = queryset.order_by("name")
    return found_clubs, searched_expression


@login_required
def profile_edit(request):
    user_id = request.user.id
    student = get_object_or_404(Student, user__pk=user_id)
    membership_club_list = Membership.objects.filter(student__user__pk=user_id)
    context = {
        "student": student,
        "membership_club_list": membership_club_list,
    }

    if request.method == "POST":
        if "Annuler" in request.POST:
            return redirect("social:profile")
        elif "Valider" in request.POST:
            print(request.POST)
            print(request.FILES)
            form = EditProfile(
                request.POST,
                request.FILES,
                instance=Student.objects.get(user=request.user),
            )
            if form.is_valid():
                form.save()
                if "picture" in request.FILES:
                    student.picture.delete(save=False)
                return redirect("social:profile")

    else:
        form = EditProfile()
        form.fields["phone_number"].initial = student.phone_number
        form.fields["department"].initial = student.department
        form.fields["picture"].initial = student.picture
        form.fields["gender"].initial = student.gender
        form.fields["birthdate"].initial = student.birthdate
        form.fields["biography"].initial = student.biography
    context["EditProfile"] = form
    return render(request, "social/profile_edit.html", context)


@login_required
def index_clubs(request):
    all_clubs_list = Club.objects.order_by("name")
    active_clubs_list = Club.objects.filter(active=True).order_by("name")
    inactive_clubs_list = Club.objects.filter(active=False).order_by("name")
    ASSO_club_list = Club.objects.filter(label=Club.Label.ASSO, active=True).order_by(
        "name"
    )
    CLUB_club_list = Club.objects.filter(label=Club.Label.CLUB, active=True).order_by(
        "name"
    )
    LISTE_club_list = Club.objects.filter(label=Club.Label.LISTE, active=True).order_by(
        "name"
    )
    POLE_club_list = Club.objects.filter(label=Club.Label.POLE, active=True).order_by(
        "name"
    )
    context = {
        "all_clubs_list": all_clubs_list,
        "club_displayed_list": active_clubs_list,
        "inactive_clubs_list": inactive_clubs_list,
        "asso_club_list": ASSO_club_list,
        "club_club_list": CLUB_club_list,
        "liste_club_list": LISTE_club_list,
        "pole_club_list": POLE_club_list,
    }
    all_categories_list = Category.objects.order_by("name")
    context["all_categories_list"] = all_categories_list

    my_memberships_list = Membership.objects.filter(student__user__id=request.user.id)
    context["my_memberships_list"] = my_memberships_list
    return render(request, "social/index_clubs.html", context)


def get_old_members(club_id):  # Grouping old members of club_id by promos in a dict
    old_members = {}
    promos = (
        Membership.objects.filter(club__id=club_id, is_old=True)
        .values("student__promo__nickname")
        .distinct()
        .order_by("-student__promo__year")
    )  # Getting every promo nickname with old members
    for promo in promos:
        promo_nickname = promo["student__promo__nickname"]
        promo_members = Membership.objects.filter(
            club__id=club_id, is_old=True, student__promo__nickname=promo_nickname
        )
        old_members[promo_nickname] = promo_members
    return old_members


@login_required
def view_club(request, club_id):
    club = get_object_or_404(Club, pk=club_id)
    active_members = Membership.objects.filter(club__id=club_id, is_old=False)
    old_members = get_old_members(club_id)
    membership_club_list = Membership.objects.filter(
        student__user__id=request.user.id, club__pk=club_id
    )
    if not membership_club_list:  # If no match is found
        is_admin = False
    # If the user does not have the rights
    elif not membership_club_list[0].is_admin:
        is_admin = False
    else:
        is_admin = True
    context = {
        "club": club,
        "active_members": active_members,
        "old_members": old_members,
        "is_admin": is_admin,
    }
    return render(request, "social/view_club.html", context)


@login_required
def club_edit(request, club_id):
    student = get_object_or_404(Student, user__id=request.user.id)
    club = get_object_or_404(Club, pk=club_id)
    student_membership_club = Membership.objects.filter(
        student__pk=student.id, club__pk=club_id
    )
    all_active_club_memberships = Membership.objects.filter(
        club__pk=club_id, is_old=False
    )
    all_old_club_memberships = get_old_members(club_id)
    form_membership = AddMember()
    form_role = AddRole()
    if not student_membership_club:  # If no match is found
        raise PermissionDenied
    # If the user does not have the rights
    if not student_membership_club[0].is_admin:
        raise PermissionDenied

    context = {
        "student": student,
        "club": club,
        "all_active_club_memberships": all_active_club_memberships,
        "all_old_club_memberships": all_old_club_memberships,
    }

    if request.method == "POST":
        if "Annuler" in request.POST:
            return redirect("social:club_detail", club_id=club.id)

        elif "Valider" in request.POST:
            form_club = EditClub(
                request.POST,
                request.FILES,
                instance=Club.objects.get(id=club.id),
            )
            if form_club.is_valid():
                if "logo" in request.FILES:
                    club.logo.delete(save=False)
                if "background_picture" in request.FILES:
                    club.background_picture.delete(save=False)
                form_club.save()
                return redirect("social:club_detail", club_id=club.id)

        elif "Ajouter-Membre" in request.POST:
            if (
                not request.POST["student"].isdigit()
                or not request.POST["role"].isdigit()
            ):
                context["error"] = (
                    "Fais bien attention à sélectionner l'élève ET le rôle"
                )
                context["AddMember"] = AddMember()
                return render(request, "social/club_edit.html", context)

            else:
                try:
                    membership_added = Membership.objects.filter(
                        student__id=request.POST["student"], club=club
                    )
                    if membership_added:
                        membership_added = membership_added[0]
                    else:
                        membership_added = Membership.objects.create(
                            student=get_object_or_404(
                                Student, pk=request.POST["student"]
                            ),
                            club=club,
                            role=None,
                            is_admin=False,
                        )
                    form_membership = AddMember(request.POST, instance=membership_added)
                    if form_membership.is_valid():
                        form_membership.save()
                    return redirect("social:club_edit", club_id=club.id)
                except Student.DoesNotExist:
                    return redirect("social:club_edit", club_id=club.id)

        elif "Vieux" in request.POST:
            old_member = Membership.objects.get(
                club=club, student__id=request.POST["student_id"]
            )
            old_member.is_admin = False
            old_member.is_old = True
            old_member.save()
            if student.id == int(
                request.POST["student_id"]
            ):  # If the user commits sudoku
                return redirect("social:club_detail", club_id=club.id)
            else:
                return redirect("social:club_edit", club_id=club.id)

        elif "Actif" in request.POST:
            not_old_member = Membership.objects.get(
                club=club, student__id=request.POST["student_id"]
            )
            not_old_member.is_old = False
            not_old_member.save()
            return redirect("social:club_edit", club_id=club.id)

        elif "Supprimer" in request.POST:
            deleted_member = Membership.objects.get(
                club=club, student__id=request.POST["student_id"]
            )
            deleted_member.delete()
            if student.id == int(
                request.POST["student_id"]
            ):  # If the user commits sudoku
                return redirect("social:club_detail", club_id=club.id)
            else:
                return redirect("social:club_edit", club_id=club.id)

        elif "Ajouter-Role" in request.POST:
            form_role = AddRole(request.POST)
            existing_role_names = list(
                Role.objects.all().values_list("name", flat=True)
            )
            if form_role.is_valid() and (
                form_role["name"].value() not in existing_role_names
            ):
                form_role.save()
            return redirect("social:club_edit", club_id=club.id)

    else:
        form_club = EditClub()

        form_club.fields["name"].initial = club.name
        form_club.fields["nickname"].initial = club.nickname
        form_club.fields["logo"].initial = club.logo
        form_club.fields["background_picture"].initial = club.background_picture
        form_club.fields["description"].initial = club.description
        form_club.fields["active"].initial = club.active
        form_club.fields["has_fee"].initial = club.has_fee
        form_club.fields["category"].initial = [
            category.pk for category in club.category.all()
        ]

    context["EditClub"] = form_club
    context["AddMember"] = form_membership
    context["AddRole"] = form_role
    return render(request, "social/club_edit.html", context)


@login_required
def club_request(request):
    context = {}

    if request.method == "POST":
        if "Annuler" in request.POST:
            return redirect("social:club_index")
        elif "Valider" in request.POST:
            form = ClubRequestForm(
                request.POST,
            )
            if form.is_valid():
                new_request = form.save(commit=False)
                new_request.student = Student.objects.get(user__id=request.user.id)
                new_request.save()
                return redirect("social:club_index")

    else:
        form = ClubRequestForm()
    context["ClubRequest"] = form
    return render(request, "social/club_request.html", context)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def validate_student(request):
    """
    Validates a student. Only accessible by superusers and staff members.
    Expects a student_id in the POST data.
    """
    # Check if user has permission
    if not (request.user.is_superuser or request.user.is_staff):
        return Response({"error": "Permission denied"}, status=403)

    # Get student_id from request data
    student_id = request.data.get("student_id")
    if not student_id:
        return Response({"error": "student_id is required"}, status=400)

    # Get and update student
    try:
        student = get_object_or_404(Student, id=student_id)
        student.is_validated = True
        student.save()
        return Response(
            {
                "success": True,
                "message": f"Student {student.user.first_name} {student.user.last_name} has been validated",
            }
        )
    except Exception as e:
        return Response({"error": str(e)}, status=400)

from rest_framework import generics, permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.views import IsStaffOrAdmin
from apps.users.models import User
from apps.users.serializers import LoginSerializer, RegisterSerializer, UserSerializer


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = Token.objects.get(user=user)
        return Response({"user": UserSerializer(user).data, "token": token.key}, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, _ = Token.objects.get_or_create(user=user)
        return Response({"user": UserSerializer(user).data, "token": token.key})


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class UserListView(generics.ListAPIView):
    """Solo admin: listado completo de usuarios."""
    serializer_class = UserSerializer
    permission_classes = [IsStaffOrAdmin]

    def get_queryset(self):
        qs = User.objects.all().order_by("-date_joined")
        role = self.request.query_params.get("role")
        if role:
            qs = qs.filter(role=role)
        return qs


class UserRoleUpdateView(APIView):
    """Solo admin: cambia el rol de un usuario."""
    permission_classes = [IsStaffOrAdmin]

    VALID_ROLES = {r[0] for r in User.Roles.choices}

    def patch(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({"detail": "Usuario no encontrado."}, status=status.HTTP_404_NOT_FOUND)

        new_role = request.data.get("role")
        if not new_role or new_role not in self.VALID_ROLES:
            return Response(
                {"detail": f"Rol inválido. Opciones: {', '.join(self.VALID_ROLES)}."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.role = new_role
        user.save(update_fields=["role"])
        return Response(UserSerializer(user).data)

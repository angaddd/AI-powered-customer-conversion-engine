from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import AllowAny

from apps.companies.serializers import CompanySerializer
from apps.companies.tenant import get_user_company
from .serializers import RegisterSerializer


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "User registered successfully"},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MeView(APIView):
    def get(self, request):
        company = get_user_company(request.user)
        return Response({
            "id": request.user.id,
            "email": request.user.email,
            "username": request.user.username,
            "company": CompanySerializer(company).data if company else None,
        })

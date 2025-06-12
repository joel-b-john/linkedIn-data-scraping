from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiResponse
from .linkedin import login_and_get_cookies, fetch_profile_data, load_cookies_if_valid

class LinkedInProfileView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'email': {'type': 'string'},
                    'password': {'type': 'string'}
                },
                'required': ['email', 'password']
            }
        },
        responses={
            200: OpenApiResponse(description="Profile and connections fetched"),
            400: OpenApiResponse(description="Missing credentials"),
            500: OpenApiResponse(description="Server error"),
        },
        description="Login to LinkedIn and fetch profile using Voyager API"
    )
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({'error': 'Missing LinkedIn credentials'}, status=400)

        try:
            # Try to load existing valid cookies
            cookies = load_cookies_if_valid(email)

            # If not available or expired, login again
            if not cookies:
                cookies = login_and_get_cookies(email, password)

            profile_data = fetch_profile_data(cookies)
            return Response(profile_data)

        except Exception as e:
            return Response({'error': str(e)}, status=500)

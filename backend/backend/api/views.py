from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from urllib.parse import urlencode
from rest_framework import status, generics
import sys
import os
import requests

from .serializers import RegisterSerializer, UserDataSerializer, UserDataPredictionSerializer, AllUserDataSerializer
from .models import UserData

root_dir = os.path.abspath(__file__)
for _ in range(4):  # Move up 4 levels
    root_dir = os.path.dirname(root_dir)

# Add the ml_models directory to sys.path
sys.path.append(os.path.join(root_dir, 'ml_models'))

# Now we can import from ml_models
from mymodels import assessment_model

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key, 'user': serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated] # Require Login

    def post(self, request):
        request.user.auth_token.delete()  # Delete the user's token
        return Response({"message": "Logged out successfully"}, status=200)

class AssessmentView(APIView):
    permission_classes = [IsAuthenticated]  # Require login

    def post(self, request):
        # Manually assign the user to the request data
        data = request.data.copy()
        data['user'] = request.user.id

        # Extract values from 'skills' and create a list
        skills_values = list(data['skills'].values())

        # You can also include 'domain' and 'experience' if needed
        # If you want them to be part of the list as well
        response_list = skills_values + [data['domain'], data['experience']]

         # Check for an existing UserData instance with the same user, domain, and experience
        user_data_instance = UserData.objects.filter(
            user=request.user
        ).first()

        # If found, update the existing instance; if not, create a new one
        if user_data_instance:
            serializer = UserDataSerializer(user_data_instance, data=data, partial=True)
        else:
            serializer = UserDataSerializer(data=data)


        # Validate and save if valid
        if serializer.is_valid():
            user_data = serializer.save()  # Saves the instance of UserData

            model_status = assessment_model.get_model_data()
            model_response = assessment_model.get_pred_data(response_list)

            # Ensure model_response data types match expected fields
            prediction_data = {
                "predicted_proficiency": str(model_response[0]) if model_response[0] is not None else None,
                "predicted_job_role": str(model_response[1]) if model_response[1] is not None else None,
                "predicted_average_score": float(model_response[2]) if model_response[2] is not None else None,
            }
            prediction_serializer = UserDataPredictionSerializer(
                user_data, data=prediction_data, partial=True
            )
            if prediction_serializer.is_valid():
                print("Data saved...")
                prediction_serializer.save()
            else:
                print("Invalid serializer", prediction_serializer.errors)

            return Response({
                    "model_status": {
                        "accuracy_proficiency": model_status[0],
                        "accuracy_job_role": model_status[1],
                        "mse_avg_score": model_status[2]
                    },
                    "assessment_result": {
                        "predicted_proficiency": model_response[0],
                        "predicted_job_role": model_response[1],
                        "predicted_average_score": model_response[2],
                        "message":model_response[3],
                    },
                }, status=status.HTTP_202_ACCEPTED)
            # return Response({"message":"success"}, status=status.HTTP_201_CREATED)
        
        # Return validation errors if invalid
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class FindJobsView(APIView):
    permission_classes = [IsAuthenticated]  # Require Login

    def post(self, request):
        try:
            # Try to fetch user domain. If it doesn't exist, fallback to a default.
            user_domain = UserData.objects.filter(user=request.user).last()
            user_domain = user_domain.domain if user_domain else "web developer"  # Default if domain is not found
        except Exception as e:
            # If there's an error fetching the user domain, use a default value
            user_domain = "web developer"  # Default to 'web developer'

        # Step 1: Get query parameters from the POST data or set defaults
        sort_by = request.data.get("sort_by", "relevance")  # Default to 'relevance'
        what = request.data.get("what", user_domain)       # Default to user domain or fallback to 'web developer'
        where = request.data.get("where", "remote")         # Default to 'remote'
        page_no = request.data.get("page", 1)               # Default to first page

        print(f"User domain: {user_domain}")

        # Step 2: Construct the URL with dynamic parameters
        params = {
            "app_id": "5aaf8801",
            "app_key": "a80271a77fd093b87a5b20c31e58ee26",
            "results_per_page": 12,
            "what": what,
            "where": where,
            "sort_by": sort_by,
        }

        # Encode URL with parameters
        base_url = f"https://api.adzuna.com/v1/api/jobs/gb/search/{page_no}"
        encoded_url = f"{base_url}?{urlencode(params)}"  # Correct URL encoding

        # Print the encoded URL to the terminal
        print(f"Encoded URL: {encoded_url}")

        try:
            # Step 3: Make the API request
            external_response = requests.get(encoded_url)
            external_response.raise_for_status()  # Raise an error for bad responses
            
            # Step 4: Process the response data
            data = external_response.json()
            jobs_data = data.get('results', [])

            # Step 5: Return the jobs list as the response
            return Response({
                "jobs": jobs_data,
                "what": what,  # Send the 'what' parameter back to frontend
            }, status=status.HTTP_200_OK)

        except requests.exceptions.RequestException as e:
            # Handle any errors during the API request
            return Response({"error": f"Failed to fetch jobs from external API: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)


class UserDataAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user_data = UserData.objects.filter(user=request.user).last()
            serializer = AllUserDataSerializer(user_data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except UserData.DoesNotExist:
            return Response({"error": "User data not found"}, status=status.HTTP_404_NOT_FOUND)

    # def post(self, request):
    #     serializer = AllUserDataSerializer(data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class FindPlaylist(APIView):
#     def get(self, request, *args, **kwargs):
#         query = self.kwargs['q']  # Access the 'q' parameter from the URL
#         api_key = ""
#         url = (
#             f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={query}&type=playlist&maxResults=10&key=AIzaSyAER_WNaquXD_zb5ye0H7qU9oZPjBS8pbM"
#         )
#         try:
#             external_response = requests.get(url)
#             external_response.raise_for_status()  # Raise an error for bad responses
            
#             data = external_response.json()  # Parse JSON response
#             playlist_data = data.get('items', [])

#             formatted_playlist = []
#             for playlist in playlist_data:
#                 snippet = playlist.get('snippet', {})
#                 id_info = playlist.get('id', {})
                
#                 playlist_id = id_info.get('playlistId')
#                 formatted_playlist.append({
#                     "title": snippet.get('title'),
#                     "thumbnail": snippet.get('thumbnails', {}).get('high', {}).get('url'),
#                     "channelTitle": snippet.get('channelTitle'),
#                     "publishedAt": snippet.get('publishedAt'),
#                     "link": f"https://www.youtube.com/playlist?list={playlist_id}",  # Constructed playlist link
#                 })

#             return Response(formatted_playlist, status=status.HTTP_200_OK)

#         except requests.exceptions.RequestException as e:
#             # Handle any errors that occur during the API request
#             return Response({"error": f"Failed to fetch playlists from external API: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

class FindPlaylist(APIView):
    def post(self, request, *args, **kwargs):
        query = self.kwargs['q']  # Access the 'q' parameter from the URL
        
        url = (
            f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={query}&type=playlist&maxResults=10&key=AIzaSyAER_WNaquXD_zb5ye0H7qU9oZPjBS8pbM"
        )
        try:
            external_response = requests.get(url)
            external_response.raise_for_status()  # Raise an error for bad responses
            
            # Send full response data directly to the client
            data = external_response.json()  # Parse JSON response
            return Response(data.get('items', []), status=status.HTTP_200_OK)

        except requests.exceptions.RequestException as e:
            # Handle any errors during the API request
            return Response({"error": f"Failed to fetch playlists from external API: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

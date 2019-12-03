from django.shortcuts import render
from base.models import *
from django.db import transaction
from rest_framework import status
from rest_framework.generics import CreateAPIView, RetrieveAPIView, DestroyAPIView, UpdateAPIView, ListAPIView, GenericAPIView
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from base.serializers import *
from base.authentication import MyAuthentication
from rest_framework.decorators import authentication_classes, permission_classes
from django.utils import timezone
from django.db.models import Q
from functools import reduce
from django.db.models import Value
from django.db.models.functions import Concat
import operator, datetime

@authentication_classes([])
class UserLoginView(APIView):
	permission_classes = [AllowAny]
	serializer_class = UserLoginSerializer

	def post(self, request, *args, **kwargs):
		with transaction.atomic():
			data = request.data
			if not data:
				# Retrun error message with 400 status
				return Response({"message": "Data is required.", "status": status.HTTP_400_BAD_REQUEST}, status.HTTP_400_BAD_REQUEST)
			else:
				email = data.get('email')
				password = data.get('password')
				is_admin = True if data.get('admin') and data.get('admin').lower() == 'true' else False
				
				if not email:
					# Retrun error message with 400 status
					return Response({"message": "Email is required.","status":status.HTTP_400_BAD_REQUEST}, status.HTTP_400_BAD_REQUEST)
				
				if not password:
					# Retrun error message with 400 status
					return Response({"message": "Password is required.","status":status.HTTP_400_BAD_REQUEST}, status.HTTP_400_BAD_REQUEST)

				if is_admin:
					
					user = User.objects.filter(email = email).first()
					
					if not user:
						# Retrun error message with 400 status
						return Response({"message": "This email is not registered.","status":status.HTTP_400_BAD_REQUEST}, status.HTTP_400_BAD_REQUEST)    
					
					if not user.is_superuser:
						# Retrun error message with 400 status
						return Response({"message": "Given user is not Admin user.","status":status.HTTP_400_BAD_REQUEST}, status.HTTP_400_BAD_REQUEST)    
				
				serializer = UserLoginSerializer(data=data)
				
				# check validation of serializer data
				if not serializer.is_valid(raise_exception=False):
					if serializer.errors.get('email'):  
						error_msg = ''.join(serializer.errors['email'])
						return Response({"message": error_msg,"status":status.HTTP_400_BAD_REQUEST}, status.HTTP_400_BAD_REQUEST)

					# Retrun error message with 400 status
					return Response({"message": ''.join(serializer.errors['message']),"status":status.HTTP_400_BAD_REQUEST}, status.HTTP_400_BAD_REQUEST)

				# Generating an unique token for each user
				user = User.objects.get(email = email)
				token = Token.objects.filter(user = user).first()
				
				if not token:
					token = Token.objects.create(user = user)
				
				user.last_login = datetime.datetime.now(tz=timezone.utc)
				user.save()

				new_data = serializer.data
				
				# Adding token, first name and last name to response
				new_data['token'] = "Token " + token.key
				new_data['first_name'] = user.first_name
				new_data['last_name'] = user.last_name
				new_data["mobile"] = user.mobile
				
				# Return success message with 200 status
				return Response({"message": "User is successfully logged in.", "data": new_data,
											"status": status.HTTP_200_OK}, status.HTTP_200_OK)

# Create new user view
@authentication_classes([])
class UserCreateView(CreateAPIView):
	permission_classes = [AllowAny]
	serializer_class = UserCreateSerializer

	def create(self, request, *args, **kwargs):
		with transaction.atomic():
			if not request.data:
				# Retrun error message with 400 status
				return Response({"message": "Data is required.", "status": status.HTTP_400_BAD_REQUEST}, status.HTTP_400_BAD_REQUEST)

			if not request.data.get('email'):
				# Retrun error message with 400 status
				return Response({"message": "Email is required.", "status":status.HTTP_400_BAD_REQUEST}, status.HTTP_400_BAD_REQUEST)
			
			if not request.data.get('password'):
				# Retrun error message with 400 status
				return Response({"message": "Password is required.", "status":status.HTTP_400_BAD_REQUEST}, status.HTTP_400_BAD_REQUEST)
			
			if not request.data.get('first_name'):
				# Retrun error message with 400 status
				return Response({"message": "First name is required.", "status":status.HTTP_400_BAD_REQUEST}, status.HTTP_400_BAD_REQUEST)
			
			if not request.data.get('last_name'):
				# Retrun error message with 400 status
				return Response({"message": "Last name is required.", "status":status.HTTP_400_BAD_REQUEST}, status.HTTP_400_BAD_REQUEST)

			if not request.data.get('mobile'):
				# Retrun error message with 400 status
				return Response({"message": "Mobile number is required.", "status":status.HTTP_400_BAD_REQUEST}, status.HTTP_400_BAD_REQUEST)

			if not request.data.get('device_token'):
				# Retrun error message with 400 status
				return Response({"message": "Device token is required.","status":status.HTTP_400_BAD_REQUEST}, status.HTTP_400_BAD_REQUEST)

			serializer = self.get_serializer(data = request.data)
			
			# check validation of serializer data
			if not serializer.is_valid(raise_exception=False):
				error_msg = serializer.errors
				if serializer.errors.get('email'):
					error_msg = 'Email address is already registerd with app.'
				if serializer.errors.get('password'):
					error_msg = ''.join(serializer.errors['password'])
				if serializer.errors.get('first_name'):
					error_msg = "First name cannot have more than 20 characters."
				if serializer.errors.get('last_name'):
					error_msg = "Last name cannot have more than 20 characters."
				if serializer.errors.get('mobile'):
					error_msg = "Mobile number cannot have more than 10 characters."
				if serializer.errors.get('device_token'):
					error_msg = ''.join(serializer.errors['device_token'])

				# Retrun error message with 400 status
				return Response({"message": error_msg,"status":status.HTTP_400_BAD_REQUEST}, status.HTTP_400_BAD_REQUEST)

			self.perform_create(serializer)

			# Generating an unique token for each user
			user = User.objects.get(id = serializer.instance.get('id'))
			token, _ = Token.objects.get_or_create(user=user)
			
			data = serializer.data
			
			# Adding token to response
			data['token'] = "Token " + token.key
			
			return Response({"message": "User is created successfully.", "data": data,
										"status": status.HTTP_201_CREATED}, status.HTTP_201_CREATED)

	# saves user in database
	def perform_create(self, serializer):
		serializer.save()


# User Logout View
class UserLogoutView(APIView):
	authentication_classes = (MyAuthentication,)

	def delete(self, request, *args, **kwargs):
		return self.destroy(request, *args, **kwargs)

	def destroy(self, request, *args, **kwargs):
		# simply delete the token to force a login
		auth_token = request.META.get("HTTP_AUTHORIZATION")
		auth_token = auth_token.split(' ')[1]
		
		token = Token.objects.filter(key = auth_token).first()
		
		if token:
			token.delete()
		
		# Return success message with 200 status
		return Response({"message": "User is successfully logged out.",
									"status": status.HTTP_200_OK}, status.HTTP_200_OK)        

# Get User View
class UserGetView(RetrieveAPIView):
	serializer_class = UserGetSerializer
	authentication_classes = (MyAuthentication,)
	queryset = User.objects.all()
	lookup_field = 'id'

	def get(self, request, *args, **kwargs):
		# Fetching user with requested id
		user = User.objects.filter(id= kwargs.get('id')).first()
		if not user:
			# User not found
			response = {"message": "User is not found", "status":status.HTTP_404_NOT_FOUND}
			return Response(response, status.HTTP_404_NOT_FOUND)
		return self.retrieve(request, *args, **kwargs)

	def retrieve(self, request, *args, **kwargs):
		response = {}
		instance = self.get_object()
		serializer = self.get_serializer(instance)
		response = {'message':"User is retrieved successfully",'status':status.HTTP_200_OK,'data':serializer.data}
		return Response(response, status.HTTP_200_OK)


#Update user by id
class UserUpdateView(UpdateAPIView):
	serializer_class = UserUpdateSerializer
	authentication_classes = (MyAuthentication,)
	queryset = User.objects.all()
	lookup_field = 'id'

	def put(self, request, *args, **kwargs):	

		if not request.data.get('first_name'):
			# Retrun error message with 400 status
			return Response({"message": "First name is required", "status":status.HTTP_400_BAD_REQUEST}, status.HTTP_400_BAD_REQUEST)
		
		if not request.data.get('last_name'):
			# Retrun error message with 400 status
			return Response({"message": "Last name is required", "status":status.HTTP_400_BAD_REQUEST}, status.HTTP_400_BAD_REQUEST)

		if not request.data.get('mobile'):
			# Retrun error message with 400 status
			return Response({"message": "Mobile number is required", "status":status.HTTP_400_BAD_REQUEST}, status.HTTP_400_BAD_REQUEST)

		# Fetching project with requested id
		user = User.objects.filter(id = kwargs.get('id')).first()
		
		if not user:
			# user not found
			response = {"message": "User is not found.", "status":status.HTTP_404_NOT_FOUND}
			return Response(response, status.HTTP_404_NOT_FOUND)
		
		# Check if logged-in user is owner of project or not
		if not user.is_superuser and user.id != request.user.id:
			response = {"message": "User is not authorized to update user.", "status":status.HTTP_400_BAD_REQUEST}
			return Response(response, status.HTTP_400_BAD_REQUEST)

		instance = self.get_object()
		response = {}
		serializer = self.get_serializer(instance, data=request.data)
		
		if serializer.is_valid(raise_exception = True):
			self.perform_update(serializer)
			data = serializer.data
			data['id'] = instance.id
			response = {"message": "User is updated successfully.","data":data,"status": status.HTTP_200_OK}
			return Response(response, status.HTTP_200_OK)
		
		else:
			response = {"message": "Error while updating user.","data":serializer.data,"status":status.HTTP_400_BAD_REQUEST}
			return Response(response, status.HTTP_400_BAD_REQUEST)

	def perform_update(self, serializer):
		serializer.save()


# User delete view
class UserDeleteView(DestroyAPIView):
	authentication_classes = (MyAuthentication,)

	def delete(self, request, *args, **kwargs):
		# Fetching user with requested id
		user = User.objects.filter(id = kwargs.get('id')).first()
		
		if not user:
			# User not found
			response = {"message": "User is not found.", "status":status.HTTP_404_NOT_FOUND}
			return Response(response, status.HTTP_404_NOT_FOUND)
		
		return self.destroy(request, user,  *args, **kwargs)

	def destroy(self, request, user, *args, **kwargs):
		user.delete()
		response = {}
		response = {"message": "User is deleted successfully.", "status":status.HTTP_200_OK}
		
		return Response(response, status.HTTP_200_OK)

	def perform_destroy(self, instance):
		instance.delete()


#Change password API
class ChangePasswordView(APIView):
	authentication_classes = (MyAuthentication,)

	def post(self, request, *args, **kwargs):
		with transaction.atomic():
			if not request.data:
				# Retrun error message with 400 status
				return Response({"message": "Data is required.", "status": status.HTTP_400_BAD_REQUEST}, status.HTTP_400_BAD_REQUEST)
		
			if not request.data.get('new_password'):
				# Retrun error message with 400 status
				return Response({"message": "Password is required.", "status":status.HTTP_400_BAD_REQUEST}, status.HTTP_400_BAD_REQUEST)

			if not request.data.get('old_password'):
				# Retrun error message with 400 status
				return Response({"message": "Password is required.", "status":status.HTTP_400_BAD_REQUEST}, status.HTTP_400_BAD_REQUEST)    

			new_password = request.data.get('new_password')
			old_password = request.data.get('old_password')

			user = User.objects.filter(id = request.user.id).first()
			
			if user:
				try:
					if user.check_password(old_password):
						
						if old_password == new_password:
							return Response({"message": "Old password and new password are same.Please enter different password.", "status": status.HTTP_400_BAD_REQUEST}, status.HTTP_400_BAD_REQUEST)    
						
						user.set_password(new_password)
						user.save()
						return Response({"message": "Password changed successfully.", "status": status.HTTP_200_OK}, status.HTTP_200_OK)
					else:
						return Response({"message": "Old password is wrong.", "status": status.HTTP_400_BAD_REQUEST}, status.HTTP_400_BAD_REQUEST)
				except Exception as e:
					return Response({"message": "Error occured.", "status": status.HTTP_400_BAD_REQUEST}, status.HTTP_400_BAD_REQUEST)
			else:
				return Response({"message": "Please login to change password.", "status":status.HTTP_400_BAD_REQUEST}, status.HTTP_400_BAD_REQUEST)    

class UserList(ListAPIView):
	authentication_classes = (MyAuthentication,)
	serializer_class = UserGetSerializer
	queryset = User.objects.exclude(is_superuser = True)

	def post(self, request, *args, **kwargs):

		# Checking user is authorized to access this building or not
		if not request.user.is_superuser:
			response = {"message": "User is not authorized to access this data.", "status":status.HTTP_404_NOT_FOUND}
			return Response(response, status.HTTP_404_NOT_FOUND)

		search_param = request.data.get('search')
		search_type = request.data.get('search_type')

		if search_param:
			if search_type and search_type == 'fullname':
				self.queryset = self.queryset.annotate(search_data = Concat('first_name', Value(' '), 'last_name')).filter(search_data__icontains = search_param)               
			else:
				q_list = [
					Q(first_name__icontains = search_param),
					Q(last_name__icontains = search_param),
					Q(mobile__icontains = search_param),
					Q(email__icontains = search_param)
				]
				self.queryset = self.queryset.filter(reduce(operator.or_, q_list))

		total_record = self.queryset.count()
		self.queryset = self.queryset.order_by('-id')
	   
		serializer = self.get_serializer(self.queryset, many = True)

		json_response = {
			"users": serializer.data,
			"total": total_record
		}
		
		response = {'status' : status.HTTP_200_OK, 'message' : 'User List retrived successfully', 'data' : json_response}    
		return Response(response, status = status.HTTP_200_OK)

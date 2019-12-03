from django.db.models import Q
from rest_framework.serializers import ModelSerializer, \
									   ValidationError, \
									   EmailField
from rest_framework import serializers
from rest_framework.status import HTTP_200_OK, \
								  HTTP_400_BAD_REQUEST, \
								  HTTP_401_UNAUTHORIZED
from base.models import *


# User LOGIN Serializer
class UserLoginSerializer(ModelSerializer):
	email = EmailField(label = 'Email')

	class Meta:
		model = User
		fields = ('email','password','id')
		extra_kwargs = {
						'password': {'write_only':True}
						}
						
	def validate(self, data):
		user_obj = None
		response = {}
		email =  data.get('email', None)
		password =  data.get('password', None)
		# Fetching user with email
		user = User.objects.filter(
			Q(email=email)
		).first()
		if user:
			# User exists
			user_obj = user
		else:
			# User does not exist
			response['message'] = "This email is not registered."
			raise ValidationError(response)
		
		if user_obj:
			# Checking password is correct or not
			if not user_obj.check_password(password):
				# Incorrect password
				response['message'] = "Password is incorrect."
				raise ValidationError(response)
  
		data['id'] = user_obj.id
		return data


# User CREATE Serializer
class UserCreateSerializer(ModelSerializer):
	class Meta:
		model = User
		fields = ('email', 'password', 'id', 'first_name', 'last_name', 'mobile', 'device_token')
		extra_kwargs = {
				'password': {'write_only':True}
						}
	# Create User
	def create(self, validated_data):
		response = {}
		# Get data from validated_data
		email = validated_data['email']
		password = validated_data['password']
		first_name = validated_data['first_name']
		last_name = validated_data['last_name']
		mobile = validated_data['mobile']
		device_token = validated_data['device_token']

		# Checking the length of password
		if len(password) < 6 :
			response['status'] = HTTP_400_BAD_REQUEST
			response['message'] = "Password must contain at least 6 character."
			raise ValidationError(response)

		if len(first_name) == 0 :
			response['status'] = HTTP_400_BAD_REQUEST
			response['message'] = "First name cannot be blank."
			raise ValidationError(response)
		
		if len(last_name) == 0 :
			response['status'] = HTTP_400_BAD_REQUEST
			response['message'] = "Last name cannot be blank."
			raise ValidationError(response)                                   

		# Create User in database
		try:
			user_obj = User(
							email= email
							)
			user_obj.set_password(password)
			user_obj.first_name = first_name
			user_obj.last_name = last_name
			user_obj.mobile = mobile
			user_obj.device_token = device_token
			user_obj.save()
			validated_data['id'] = user_obj.id

		except Exception as e:
			response['status'] = HTTP_400_BAD_REQUEST
			response['message'] = "Error while creating user."
			raise ValidationError(response) 
		
		return validated_data


class UserGetSerializer(ModelSerializer):
	class Meta:
		model = User
		fields = ('id', 'first_name', 'last_name', 'email', 'mobile')


class UserUpdateSerializer(ModelSerializer):
	class Meta:
		model = User
		fields = ('first_name', 'last_name', 'mobile', 'modified_at') 


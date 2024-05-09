from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework import permissions

from .services import *
from .serializers import *
from .models import CustomUser as User
from django.db.models import Q
from rest_framework.views import APIView

# #===================================================================================================================================================================================
# class LogoutView(APIView):
#     def post(self, request):
#         try:
#             token = request.headers.get('Authorization').split(' ')[1]
#             if cache.get(token):

                
#                 return Response({"error": "Токен уже недействителен."}, status=status.HTTP_400_BAD_REQUEST)
#             cache.set(token, True, timeout=None)  # Устанавливаем токен в кэш без срока действия
#             return Response({"message": "Вы успешно вышли из системы."}, status=status.HTTP_200_OK)
#         except AttributeError:
#             return Response({"error": "Отсутствует заголовок Authorization."}, status=status.HTTP_400_BAD_REQUEST)
#         except Exception as e:
#             return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

# #отправить код на почту       

# # если user забыл пароль при входе
# class ForgetPasswordView(generics.UpdateAPIView):
#     serializer_class = ForgetPasswordSerializer

#     http_method_names = ['patch',]
#     def update(self, request, *args, **kwargs):
        
#         result = ChangePasswordOnReset.change_password_on_reset(self=self,request=request)

#         if result == "success":
#             return Response({"success ":"Пароль успешно изменен"}, status=status.HTTP_200_OK)
#         else:
#             return Response(result, status=status.HTTP_400_BAD_REQUEST)


# class MarketListAPIView(generics.ListAPIView):
#     queryset = SellerProfile.objects.prefetch_related('products').all()
#     serializer_class = MarketSerializer
#     permission_classes = [permissions.IsAuthenticated]
#     pagination_class = PageNumberPagination
#     pagination_class.page_size = 10



    

# # ===== Продавец Seller ====================================================================================================================================================================


class SellerRegisterView(CreateUserApiView):
    queryset = SellerProfile.objects.all()
    serializer_class = SellerRegisterSerializer
     


# апи для того чтобы сттать продавцом 
class BecomeSellerView(generics.CreateAPIView):
    
    # permission_classes = [permissions.IsAuthenticated]
    serializer_class = BecomeSellerSerializer
    
    
    def post(self, request, *args, **kwargs):
        user = request.user
        news_seller = SellerProfile.objects.create(
            user=user,
            is_seller=True
        )
        return Response({'success':f"Вы успешно стали продавцом"}, status=status.HTTP_200_OK)
    
# # апи для логина
class SellerLoginView(generics.CreateAPIView):
    queryset = SellerProfile.objects.all()
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        email_or_phone = request.data.get('email_or_phone')
        password = request.data.get('password')

        if not email_or_phone or not password:
            return Response({'error':'Both email/phone and password are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = SellerProfile.objects.filter(Q(email=email_or_phone) | Q(phone_number=email_or_phone)).first()

        if not user:
            return Response({'error': 'The user does not exist'}, status=status.HTTP_404_NOT_FOUND)
        
        if not check_password(password, user.password):
            return Response({'error':'Incorrect password'}, status=status.HTTP_400_BAD_REQUEST)
        
        
        refresh = RefreshToken.for_user(user=user)
        access_token = refresh.access_token
        return Response({
            'detail': 'Successfully confirmed your code',
            'id': user.id,
            'is_seller': user.is_seller,
            'email': user.email,
            'phone_number': user.phone_number,
            'refresh': str(refresh),
            'access': str(access_token),
            'refresh_lifetime_days': refresh.lifetime.days,
            'access_lifetime_seconds': access_token.lifetime.total_seconds()
        })


# # апи который проверяет код который был отправлен на указанный email и в ответ передает токен
class SellerVerifyRegisterCode(generics.UpdateAPIView):
    serializer_class = VerifyCodeSerializer

    http_method_names = ['patch',]
    def patch(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        code = serializer.validated_data.get('code')
        return CheckCode.check_code(code=code)
    


class SellerForgetPasswordSendCodeView(generics.UpdateAPIView):
    serializer_class = SendCodeSerializer
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        email_or_phone = request.data.get("email_or_phone")
        if not email_or_phone:
            return Response({"required": "email_or_phone"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = SellerProfile.objects.get(email_or_phone=email_or_phone)
            # Если пользователь уже существует, просто обновите его код подтверждения и отправьте его
            send_verification_code(email_or_phone=email_or_phone)
            return Response({"success":"Код был отправлен на почту/телефон"}, status=status.HTTP_200_OK)
        except SellerProfile.DoesNotExist:
            # Если пользователь не существует, создайте нового пользователя и отправьте ему код подтверждения
            user = SellerProfile.objects.create(email_or_phone=email_or_phone)
            send_verification_code(email_or_phone=email_or_phone)
            return Response({"success":"Код был отправлен на почту/телефон"}, status=status.HTTP_201_CREATED)



# Admin
class SellerListApiview(generics.ListAPIView):
    queryset = SellerProfile.objects.all()
    serializer_class = SellerProfileSerializer
    permission_classes = [permissions.IsAdminUser,]

    def get_queryset(self):
        seller  = self.request.user.id


class SellerDetailApiview(generics.RetrieveAPIView):
    queryset = SellerProfile.objects.all()
    serializer_class = SellerProfileDetailSerializer
    permission_classes = [permissions.IsAdminUser,]



#LOGOUT


class LogoutView(APIView):
    def post(self, request):
        try:
            refresh_token = request.data['refresh_token']
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({'detail': 'Successfully logged out.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'detail': 'Error logging out.'}, status=status.HTTP_400_BAD_REQUEST)















# # === Profile =========================================================================================================================================================


class SellerUpdateProfileShopApi(generics.RetrieveUpdateAPIView):
    queryset = SellerProfile.objects.all()
    serializer_class = SellerProfileSerializer
    http_method_names = ['patch',]
    # permission_classes = [permissions.IsAuthenticated,]
    lookup_field = 'pk'


from rest_framework.generics import GenericAPIView
from rest_framework.mixins import UpdateModelMixin
from django.contrib.auth.hashers import make_password
from app_user.models import CustomUser
from django.utils.crypto import constant_time_compare


class ChangePasswordAPIVIew(UpdateModelMixin, GenericAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        user = SellerProfile.objects.get(id=self.request.user.id)
        return user

    def patch(self, *args, **kwargs):
        serializer = self.get_serializer(data=self.request.data)
        if serializer.is_valid():
            new_password = self.request.data.get('new_password')
            confirming_new_password = self.request.data.get('confirming_new_password')
            if constant_time_compare(new_password, confirming_new_password):
                user = self.get_object()
                user.password = make_password(confirming_new_password)
                user.save()
                return Response({'Вы ушпешно поменяли свой пароль'}, status=status.HTTP_200_OK)
            else:
                return Response({'Пароли не совподают'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors)


# # апи менят пароль в профиле 
# class UserResetPasswordView(generics.UpdateAPIView):
#     serializer_class = ChangePasswordSerializer
#     permission_classes = [permissions.IsAuthenticated]

#     http_method_names = ['patch',]
#     def update(self, request, *args, **kwargs):
#             result = ChangePassword.change_password_on_profile(request=request)

#             if result == "success":
#                 return Response({"success":"Пароль успешно изменен"}, status=status.HTTP_200_OK)
#             else:
#                 return Response(result, status=status.HTTP_400_BAD_REQUEST)

# class ListProfileApi(generics.ListAPIView):
#     queryset = CustomUser.objects.all()
#     serializer_class = UserProfileSerializer



# class UpdateUserProfileApi(generics.UpdateAPIView):
#     queryset = CustomUser.objects.all()
#     serializer_class = UserProfileSerializer
#     http_method_names = ['patch',]
#     permission_classes = [permissions.IsAuthenticated,]
#     lookup_field = 'id'

# class DetailUserProfileApi(generics.RetrieveAPIView):
#     queryset = CustomUser.objects.all()
#     serializer_class = UserProfileSerializer
#     lookup_field = 'id'


#===============================================================================================================================================
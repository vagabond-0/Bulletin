from rest_framework_simplejwt.authentication import JWTAuthentication
from django.apps import apps
import logging

logger = logging.getLogger(__name__)

class AlumniJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        header = self.get_header(request)
        if header is None:
            logger.debug("No authentication header found")
            return None
        
        raw_token = self.get_raw_token(header)
        if raw_token is None:
            logger.debug("No raw token found in header")
            return None
        
        try:
            validated_token = self.get_validated_token(raw_token)
            logger.debug(f"Token validated successfully: {validated_token['jti']}")
            
            Alumni = apps.get_model('User', 'Alumni')
            alumni_id = validated_token.get("alumni_id")
            
            if not alumni_id:
                logger.warning(f"Token missing alumni_id: {validated_token}")
                return None
            
            alumni = Alumni.objects.get(pk=alumni_id)
            logger.debug(f"Found alumni: {alumni.username} (ID: {alumni.id})")
            
            # Make sure the alumni has the required attributes for authentication
            if not hasattr(alumni, 'is_authenticated'):
                alumni.is_authenticated = True
                
            # Set custom attribute to verify this authentication worked
            alumni.authenticated_by = 'jwt'
            
            return (alumni, validated_token)
            
        except Alumni.DoesNotExist:
            logger.error(f"Alumni with ID {alumni_id} does not exist")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in authenticate: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return None
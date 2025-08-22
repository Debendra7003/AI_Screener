from twilio.rest import Client
try:
    from twilio.twiml.voice_response import VoiceResponse
except ImportError:
    from twilio.twiml import VoiceResponse
from django.conf import settings
from django.utils import timezone
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


class TwilioVoiceService:
    """Service for handling Twilio voice calls and TTS/STT"""
    
    def __init__(self):
        self.client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        self.from_number = settings.TWILIO_PHONE_NUMBER
    
    def initiate_interview_call(self, to_phone: str, interview_id: str) -> Dict:
        """Initiate a voice call for interview with pre-recorded message"""
        
        # Check if phone number is whitelisted
        if to_phone not in settings.WHITELISTED_PHONE_NUMBERS:
            raise ValueError(f"Phone number {to_phone} is not whitelisted")
        
        try:
            # Create simple TwiML message without webhooks
            twiml_message = """
            <Response>
                <Say voice="alice">
                    Hello! Thank you for applying to our position. 
                    We have received your application and our AI system has generated 
                    interview questions based on your profile. 
                    Our team will review your application and contact you within 
                    24 hours to schedule a detailed interview. 
                    Thank you for your interest in joining our company. 
                    Have a great day!
                </Say>
            </Response>
            """
            
            call = self.client.calls.create(
                to=to_phone,
                from_=self.from_number,
                twiml=twiml_message.strip(),
                timeout=30
            )
            
            logger.info(f"Call initiated: {call.sid} to {to_phone}")
            
            return {
                'call_sid': call.sid,
                'status': call.status,
                'to': to_phone,
                'from': self.from_number,
                'message': 'Pre-recorded message call initiated successfully'
            }
            
        except Exception as e:
            logger.error(f"Error initiating call: {e}")
            raise
    
    def generate_interview_twiml(self, questions: List[str], current_question_index: int = 0) -> str:
        """Generate TwiML for interview questions"""
        
        response = VoiceResponse()
        
        if current_question_index == 0:
            # Welcome message
            response.say(
                "Hello! Thank you for participating in this AI-powered interview. "
                "I will ask you several questions. Please answer clearly after each beep. "
                "Let's begin with the first question.",
                voice='alice'
            )
        
        if current_question_index < len(questions):
            question = questions[current_question_index]
            
            # Ask the question
            response.say(question, voice='alice')
            
            # Record the answer
            response.record(
                max_length=120,  # 2 minutes max per answer
                finish_on_key='#',
                transcribe=True,
                transcribe_callback=f"/api/voice/webhook/transcription/{current_question_index}/",
                action=f"/api/voice/webhook/next-question/{current_question_index + 1}/",
                method='POST'
            )
        else:
            # End of interview
            response.say(
                "Thank you for completing the interview. "
                "We will review your responses and get back to you soon. "
                "Have a great day!",
                voice='alice'
            )
            response.hangup()
        
        return str(response)
    
    def generate_simple_twiml(self, message: str) -> str:
        """Generate simple TwiML response"""
        response = VoiceResponse()
        response.say(message, voice='alice')
        return str(response)
    
    def get_call_details(self, call_sid: str) -> Dict:
        """Get call details from Twilio"""
        try:
            call = self.client.calls(call_sid).fetch()
            return {
                'sid': call.sid,
                'status': call.status,
                'duration': call.duration,
                'start_time': call.start_time,
                'end_time': call.end_time,
                'from': call.from_,
                'to': call.to
            }
        except Exception as e:
            logger.error(f"Error fetching call details: {e}")
            return {}
    
    def get_call_recordings(self, call_sid: str) -> List[Dict]:
        """Get recordings for a call"""
        try:
            recordings = self.client.recordings.list(call_sid=call_sid)
            return [
                {
                    'sid': recording.sid,
                    'duration': recording.duration,
                    'url': f"https://api.twilio.com{recording.uri.replace('.json', '.mp3')}",
                    'date_created': recording.date_created
                }
                for recording in recordings
            ]
        except Exception as e:
            logger.error(f"Error fetching recordings: {e}")
            return []
    
    def validate_phone_number(self, phone_number: str) -> bool:
        """Validate if phone number is in E.164 format and whitelisted"""
        import re
        
        # Check E.164 format
        e164_pattern = r'^\+[1-9]\d{1,14}$'
        if not re.match(e164_pattern, phone_number):
            return False
        
        # Check if whitelisted
        return phone_number in settings.WHITELISTED_PHONE_NUMBERS
    
    def initiate_simple_notification_call(self, to_phone: str, candidate_name: str = "Candidate") -> Dict:
        """Initiate a simple notification call with pre-recorded message"""
        
        # Check if phone number is whitelisted
        if to_phone not in settings.WHITELISTED_PHONE_NUMBERS:
            raise ValueError(f"Phone number {to_phone} is not whitelisted")
        
        try:
            # Create simple TwiML message
            twiml_message = f"""
            <Response>
                <Say voice="alice">
                    Hello {candidate_name}! Thank you for applying to our position. 
                    We have received your application and our AI system has generated 
                    interview questions based on your profile. 
                    Our team will review your responses and contact you within 
                    24 to 48 hours with the next steps. 
                    Thank you for your interest in joining our company. 
                    Have a great day!
                </Say>
            </Response>
            """
            
            call = self.client.calls.create(
                to=to_phone,
                from_=self.from_number,
                twiml=twiml_message.strip(),
                timeout=30
            )
            
            logger.info(f"Notification call initiated: {call.sid} to {to_phone}")
            
            return {
                'call_sid': call.sid,
                'status': call.status,
                'to': to_phone,
                'from': self.from_number,
                'message': 'Notification call initiated successfully'
            }
            
        except Exception as e:
            logger.error(f"Error initiating notification call: {e}")
            raise


class SpeechToTextService:
    """Service for handling speech-to-text conversion"""
    
    def process_transcription(self, recording_url: str) -> str:
        """Process audio recording and return transcript"""
        # Twilio provides automatic transcription
        # This method can be enhanced with additional STT services if needed
        try:
            # For now, we rely on Twilio's built-in transcription
            # In production, you might want to use Google Speech-to-Text or AWS Transcribe
            return "Transcription will be provided by Twilio webhook"
        except Exception as e:
            logger.error(f"Error processing transcription: {e}")
            return ""


class TextToSpeechService:
    """Service for handling text-to-speech conversion"""
    
    def generate_speech_url(self, text: str) -> str:
        """Generate speech from text (handled by Twilio TwiML)"""
        # Twilio handles TTS through the Say verb in TwiML
        # This method can be used for pre-generating audio files if needed
        return ""

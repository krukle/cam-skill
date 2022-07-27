import os
import base64
from mycroft.messagebus     import Message
from mycroft                import MycroftSkill, intent_handler
from threading              import Timer
from mailjet_rest           import Client

class Cam(MycroftSkill):
    def __init__(self):
        """Initialize the object for mycroft.
        """      
        MycroftSkill.__init__(self)

    def initialize(self):
        """Initialize event listeners.
        """
        self.add_event('cam-skill:selfie_taken', self.selfie_taken_handler)
        self.selfie = None
        self.timer = Timer(120, self.exit_cam)
        self.disable_timed_intents()

    def disable_timed_intents(self):
        self.disable_intent('delete.selfie.intent')
        self.disable_intent('another.selfie.intent')
        self.disable_intent('send.selfie.intent')
        self.disable_intent('exit.cam.intent')
        self.timer.cancel()

    def enable_timed_intents(self, time:int):
        self.enable_intent('delete.selfie.intent')
        self.enable_intent('another.selfie.intent')
        self.enable_intent('send.selfie.intent')      
        self.enable_intent('exit.cam.intent')      
        self.timer.cancel()
        self.timer = Timer(time, self.exit_cam)
        self.timer.start()

    def selfie_taken_handler(self, message:Message):
        """This method is called when the user takes a selfie.

        Args:
            message (Message): 
                Message from MagicMirror containing 'data' dict 
                
                with path to selfie with key 'selfie' and 
                
                duration in which resulting selfie should be shown before 
                
                exiting with key 'resultDuration'. 
        """
        assert message.data['selfie'], "No path to selfie found."
        self.selfie = message.data['selfie']
        self.enable_timed_intents(message.data['resultDuration'] or 120)
        self.speak_dialog('do.you.want.to.delete.another.save.or.exit')

    def send_selfie(self):
        """Send a selfie to a friend .
        """
        self.log.info("Sending selfie")
        with open(self.selfie, "rb") as file:
            base64_selfie = base64.b64encode(file.read()).decode()

        api_key = os.environ['MJ_APIKEY_PUBLIC']
        api_secret = os.environ['MJ_APIKEY_PRIVATE']
                        
        mailjet = Client(auth=(api_key, api_secret), version='v3.1')
        data = {
            'Messages': [{
                "From": {
                    "Email": "smartspegel@outlook.com",
                    "Name": "Smart"
                },
                "To": [{
                    "Email": "kriilla96@gmail.com",
                    "Name": "Christoffer"
                }],
                "Subject": "Selfie sent from MagicMirror",
                "TextPart": "This is a selfie sent to you from the MagicMirror!",
                "HTMLPart": "<h3>Hello friend!</h3><br />Here's a picture of me!",
                'InlinedAttachments': [{
                    "ContentType": "image/jpeg",
                    "Filename": "selfie.jpeg",
                    "ContentID": "id1",
                    "Base64Content": base64_selfie,
                }],
            }]
        }
        result = mailjet.send.create(data=data)
        self.log.info(result.status_code)
        self.log.info(result.json())

    def delete_selfie(self):
        """Delete selfie .
        """
        os.remove(self.selfie)
        self.exit_cam()
        self.speak_dialog('selfie.deleted')
    
    def exit_cam(self):
        self.disable_timed_intents()
        self.emit_exit_cam()
                
    def emit_take_selfie(self):
        """Emits the TAKE-SELFIE command to MMM-Cam.
        """
        self.bus.emit(Message("RELAY:MMM-Cam:TAKE-SELFIE", {
            "option": {
                "shootCountdown": 3,
                "playShutter": True,
                "displayCountdown": True,
            }
        }))
 
    def emit_exit_cam(self):
        """Emits the EXIT-CAM command to MMM-Cam.
        """
        self.bus.emit(Message("RELAY:MMM-Cam:EXIT-CAM", {}))

    @intent_handler('take.a.selfie.intent')
    def selfie_intent(self):
        """Listen for user intent to init cam and init cam.
        """
        self.log.info("take selfie")
        return self.emit_take_selfie()
    
    @intent_handler('delete.selfie.intent')
    def delete_selfie_timed_intent(self):
        self.log.info("delete selfie")
        if self.ask_yesno('are.you.sure.you.want.to.delete.selfie') == 'yes':
            return self.delete_selfie()
        self.speak_dialog('selfie.not.deleted')
        
    @intent_handler('another.selfie.intent')
    def another_selfie_timed_intent(self):
        self.log.info("another selfie")
        self.exit_cam()
        return self.emit_take_selfie()
    
    @intent_handler('send.selfie.intent')
    def send_selfie_timed_intent(self):
        self.exit_cam()
        return self.send_selfie()
    
    @intent_handler('exit.cam.intent')
    def exit_cam_timed_intent(self):
        self.log.info("exit cam")
        self.speak_dialog('exiting.cam')
        return self.exit_cam()

def create_skill() -> Cam:
    return Cam()
from mycroft.messagebus     import Message
from mycroft                import MycroftSkill, intent_handler

class Cam(MycroftSkill):
    def __init__(self):
        """Initialize the object for mycroft.
        """      
        MycroftSkill.__init__(self)

    def initialize(self):
        """Initialize event listeners.
        """
        self.add_event('cam-skill:selfie_taken', self.selfie_taken_handler)

    def selfie_taken_handler(self, message:Message):
        """This method is called when the user takes a selfie.

        Args:
            message (Message): Message from MagicMirror containing 'data' dict with path to selfie with key 'selfie'. 
        """
        print(message.data['selfie'])
        assert message.data['selfie'], "No path to selfie found."
        selfie = message.data['selfie']
        self.log.info('Selfie taken notification received.')
        while True:
            options = self.translate_namedvalues('options')
            selection = self.ask_selection(options.items(), 'what.to.do')
            if selection == options['another']:
                return self.emit._take_selfie()
            elif selection == options['send']:
                self.send_selfie(selfie)
                return self.another_selfie()
            elif selection == options['delete']:
                self.delete_selfie(selfie)
                return self.another_selfie()
            elif selection == options['exit'] or self.ask_yes_no('did.not.understand.do.you.want.to.exit') == 'yes':
                return self.exit_cam()
            
    def another_selfie(self):
        """Ask the user if they want to take another selfie.
        """
        if self.ask_yes_no('another.selfie') == 'yes':
            self.acknowledge()
            return self.emit_take_selfie()
        self.acknowledge()

    def send_selfie(self, selfie:str):
        """Send a selfie to a friend .

        Args:
            selfie (str): Path to selfie.
        """
        self.log.info("FILE SHOULD BE SENT HERE")
    
    def delete_selfie(self, selfie:str):
        """Delete selfie .
        """
        self.log.info("FILE SHOULD BE DELETED HERE")
        
    def exit_cam(self):
        """Exit the camera.
        """
        self.acknowledge()
        self.emit_exit_cam()
         
    def emit_take_selfie(self):
        """Emits the TAKE-SELFIE command to MMM-Cam.
        """
        self.bus.emit(Message("RELAY:MMM-Cam:TAKE-SELFIE", {}))
 
    def emit_init_cam(self):
        """Emits the INIT-CAM command to MMM-Cam.
        """
        self.bus.emit(Message("RELAY:MMM-Cam:INIT-CAM", {}))
        
    def emit_exit_cam(self):
        """Emits the EXIT-CAM command to MMM-Cam.
        """
        self.bus.emit(Message("RELAY:MMM-Cam:EXIT-CAM", {}))

    @intent_handler('take.a.selfie.intent')
    def selfie_intent(self):
        """Listen for user intent to init cam and init cam.
        """
        return self.emit_init_cam()

def create_skill() -> Cam:
    return Cam()
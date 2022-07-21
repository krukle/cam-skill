from mycroft.messagebus     import Message
from mycroft                import MycroftSkill, intent_handler

class Cam(MycroftSkill):
    def __init__(self):
        """Initialize the object for mycroft.
        """      
        MycroftSkill.__init__(self)  
        pass

    def initialize(self):
        """Initialize event lsiteners.
        """
        self.add_event('cam-skill:selfie_taken', self.selfie_taken_handler())
 
    def selfie_taken_handler(self, selfie:bytes):
        """This function is called when the user takes a selfie.
        """
        while True:
            selection = self.ask_selection(self.translate_list('selfie.options'))
            if selection in self.translate_list('only.save.selfie'):
                self.save_selfie(selfie)
                return self.another_selfie()
            elif selection in self.translate_list('save.and.send.selfie'):
                self.send_selfie(selfie)
                return self.another_selfie()
            elif selection in self.translate_list('delete.selfie'):
                self.delete_selfie()
                return self.another_selfie()
            elif selection in self.translate_list('exit') or self.ask_yes_no('did.not.understand.do.you.want.to.exit') == 'yes':
                return self.exit_cam()
            
    def another_selfie(self):
        """Ask the user if the want to take another selfie.
        """
        if self.ask_yes_no('another.selfie') == 'yes':
            return self.emit_take_selfie()
                
    def save_selfie(self, selfie:bytes):
        """Save the selfie to disk .

        Args:
            selfie (bytes): The selfie.
        """
        pass
    
    def send_selfie(self, selfie:bytes):
        """Send a selfie to a friend .

        Args:
            selfie (bytes): The selfie.
        """
        self.save_selfie(selfie)
        pass
    
    def delete_selfie(self):
        """Delete selfie .
        """
        pass
 
    def emit_take_selfie(self):
        """Emits the TKE - IKE - self - self .
        """
        self.bus.emit(Message("RELAY:MMM-Cam:TAKE-SELFIE", {}))
 
    def emit_init_cam(self):
        """Emits the INIT - CAM for the device .
        """
        self.bus.emit(Message("RELAY:MMM-Cam:INIT-CAM", {}))

    @intent_handler('take.a.selfie')
    def selfie_intent(self):
        """Listen for user intent to init cam and init cam.
        """
        return self.emit_init_cam()

def create_skill() -> Cam:
    return Cam()
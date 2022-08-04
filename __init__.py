import os
import base64
from mycroft.messagebus import Message
from mycroft import MycroftSkill, intent_handler
from mycroft.skills.api import SkillApi
from threading import Timer
from mailjet_rest import Client


class Cam(MycroftSkill):
    def __init__(self):
        """
        Initialize the skill.
        """
        MycroftSkill.__init__(self)

    def initialize(self):
        """
        Initialize the selfie intent. Set the last saved selfie to None, and set the timer to 120 seconds.
        """
        self.add_event('cam-skill:selfie_taken', self.selfie_taken_handler)
        self.selfie = None
        self.timer = Timer(120, self.exit_cam)
        self.disable_timed_intents()

    def selfie_taken_handler(self, message: Message):
        """
        Handle the selfie taken message. This is the first message we receive when a selfie is taken.
        @param message - the message containing the selfie path and duration is which to show the resulting selfie.
        """
        assert message.data['selfie'], "No path to selfie found."
        self.selfie = message.data['selfie']
        self.enable_timed_intents(message.data['resultDuration'] or 120)
        self.speak_dialog('do.you.want.to.delete.another.save.or.exit')

    def disable_timed_intents(self):
        """
        Disable the timed intents and cancel the timer.
        """
        self.disable_intent('delete.selfie.intent')
        self.disable_intent('another.selfie.intent')
        self.disable_intent('send.selfie.intent')
        self.disable_intent('exit.cam.intent')
        self.timer.cancel()

    def enable_timed_intents(self, time: int):
        """
        Enable the timed intents and set the timer to the time parameter.
        @param time - the time parameter           
        """
        self.enable_intent('delete.selfie.intent')
        self.enable_intent('another.selfie.intent')
        self.enable_intent('send.selfie.intent')
        self.enable_intent('exit.cam.intent')
        self.timer.cancel()
        self.timer = Timer(time, self.exit_cam)
        self.timer.start()

    def send_selfie(self, contact: dict):
        """
        Send a selfie to the contact.
        @param contact - the contact to send the selfie to.
        """
        self.log.info("Sending selfie")

        with open(self.selfie, "rb") as file:
            base64_selfie = base64.b64encode(file.read()).decode()

        api_key = "059fd1118e8d1ecab417cbf62c881ed6"
        api_secret = "a011215abe3f3bcdaeccbdf944f1d185"

        mailjet = Client(auth=(api_key, api_secret), version='v3.1')
        data = {
            'Messages': [{
                "From": {
                    "Email": "smartspegel@outlook.com",
                    "Name": "Smartspegel"
                },
                "To": [{
                    "Email": contact["email"],
                    "Name": contact["name"]
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

    def get_contact(self, name: str) -> dict:
        """
        Ask the user for a contact.
        @param name - the name of the contact           
        @return the contact if found, otherwise None
        """
        best_match = SkillApi.get("contacts-skill").get_best_match(name)
        if not best_match or len(best_match) <= 0:
            self.speak_dialog("could.not.find.contact", {"name": name})
            return None
        elif len(best_match) == 1:
            contact = {
                "name": best_match[0][0], "email": best_match[0][1], "phone": best_match[0][2]}
        else:
            selection = self.ask_selection(
                [x[2] for x in best_match], "choose.contact")
            selected = [(name, email, phone) for (
                name, email, phone, score) in best_match if phone == selection]
            if len(selected) == 1:
                contact = {
                    "name": selected[0][0], "email": selected[0][1], "phone": selected[0][2]}
            else:
                return None
        if self.ask_yesno("do.you.want.to.send.selfie.to", contact) == "yes":
            return contact
        return None

    def delete_selfie(self):
        """
        Delete the selfie and exit the camera.
        """
        os.remove(self.selfie)
        self.exit_cam()
        self.speak_dialog('selfie.deleted')

    def exit_cam(self):
        """
        Exit the camera.
        """
        self.disable_timed_intents()
        self.emit_exit_cam()

    def emit_take_selfie(self):
        """
        Emit a message to the MMM-Cam module to take a selfie.
        """
        self.bus.emit(Message("RELAY:MMM-Cam:TAKE-SELFIE", {
            "option": {
                "shootCountdown": 3,
                "playShutter": True,
                "displayCountdown": True,
            }
        }))

    def emit_exit_cam(self):
        """
        Emit a message to the MMM-Cam module to exit the camera.
        """
        self.bus.emit(Message("RELAY:MMM-Cam:EXIT-CAM", {}))

    @intent_handler('take.a.selfie.intent')
    def selfie_intent(self):
        """
        This function is called when the user says "take a selfie". It will take a selfie and return a response.
        """
        self.log.info("take selfie")
        return self.emit_take_selfie()

    @intent_handler('delete.selfie.intent')
    def delete_selfie_timed_intent(self):
        """
        This function is called when the user says "delete selfie". Deletes the selfie.
        """
        self.log.info("delete selfie")
        if self.ask_yesno('are.you.sure.you.want.to.delete.selfie') == 'yes':
            return self.delete_selfie()
        self.speak_dialog('selfie.not.deleted')

    @intent_handler('another.selfie.intent')
    def another_selfie_timed_intent(self):
        """
        When the user says "another selfie" we exit the camera and take a new selfie.
        """
        self.log.info("another selfie")
        self.exit_cam()
        return self.emit_take_selfie()

    @intent_handler('send.selfie.to.intent')
    def send_selfie_timed_intent(self, msg):
        """
        This function is called when the user says "send selfie to ____". Sends a selfie to a contact.
        @param contact_name - the contact to send the selfie to
        """
        contact_name = msg.data["contact_name"]
        contact = self.get_contact(contact_name if contact_name else self.get_response(
            'who.do.you.want.to.send.it.to'))
        if contact is not None:
            self.exit_cam()
            return self.send_selfie(contact)
        return
    
    @intent_handler('send.selfie.intent')
    def send_selfie_timed_intent(self, msg):
        """
        This function is called when the user says "send selfie". Sends a selfie to a contact.
        """
        contact_name = self.get_response('who.do.you.want.to.send.it.to')
        if contact_name is None:
            return
        contact = self.get_contact(contact_name)
        if contact is None:
            return
        self.exit_cam()
        return self.send_selfie(contact)

    @intent_handler('exit.cam.intent')
    def exit_cam_timed_intent(self):
        """
        This function is called when the user says "exit cam". Exits the camera session.
        """
        self.log.info("exit cam")
        self.speak_dialog('exiting.cam')
        return self.exit_cam()


def create_skill() -> Cam:
    return Cam()

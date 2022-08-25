# <img src='https://raw.githubusercontent.com/FortAwesome/Font-Awesome/6.x/svgs/solid/camera-retro.svg' card_color='#40db60' width='50' height='50' style='vertical-align:bottom'/> Take a photo

Mycroft skill used to take a photo with your webcam and then show it on the MagicMirror.

## Dependencies

```bash
mycroft-pip install mailjet-rest
git clone git@github.com:oenstrom/contacts-skill.git ~/mycroft-core/skills/contacts-skill
git clone git@github.com:oenstrom/MMM-mycroft-bridge.git ~/MagicMirror/modules/MMM-mycroft-bridge
git clone git@github.com:krukle/MMM-Cam.git ~/MagicMirror/modules/MMM-Cam
npm --prefix ~/MagicMirror/modules/MMM-Cam install ~/MagicMirror/modules/MMM-Cam
```

> **Note**
>
> Change git clone destination according to your setup.

## Messages

### Emitted

| Message | Data | About |
| ------- | ---- | ----- |
| TAKE-SELFIE | `{"option": {"shootCountdown": int, "playShutter": boolean, "displayCountdown": boolean}}` | Emitted when a photo is to be taken. |
| EXIT-CAM | `{}` | Emitted to tell MMM-Cam to close camera. |

### Subscribed

| Message | Data | About |
| ------- | ---- | ----- |
| cam-skill:selfie_taken | `str:` Path to selfie | Received when a photo is taken. |

## Commands

### Take a photo

Take a selfie by saying one of the following phrases.

| English | Swedish |
| ------- | ------- |
| "Take a photo" | "Ta en bild" |
| "Take a selfie" | "Ta en selfie" |

When a selfie's been taken. The *delete*, *send* and *exit* intents are activated.

#### Delete photo

| English | Swedish |
| ------- | ------- |
| "Delete photo" | "Radera bilden" |
| "Remove selfie" | "Ta bort selfien" |

#### Send photo

| English | Swedish |
| ------- | ------- |
| "Send photo" | "Skicka bilden" |
| "Email selfie" | "Mejla selfien" |
| "Send photo to `contact`" | "Skicka bilden till `contact`" |

If `contact` is emitted, mycroft will ask for `contact`.

#### Exit camera

| English | Swedish |
| ------- | ------- |
| "Exit camera" | "Avsluta kamera" |
| "Quit selfie mode" | "Stäng av selfieläge" |

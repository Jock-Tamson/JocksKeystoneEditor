import os

from Keystone.Reference.ColorDictionary import STANDARD_COLOR_DICTIONARY
from Keystone.Utility.KeystoneUtils import (CompareKeybindStrings, ParseBracketedCodes,
                                            RemoveOuterQuotes)

LOAD_FILE_COMMANDS = ("bind_load_file", "bind_load_file_silent")

#constant strings
TOGGLE_STR = "++"
REPEAT_STR = "+"
COLOR_STR = "color"
BACKGROUND_STR = "bgcolor"
BORDER_STR = "bordercolor"
SCALE_STR = "scale"
DURATION_STR = "duration"

#object for a single slash command
class SlashCommand():

    #parse name and text from a string
    def Parse(self, repr: str):

        #split on space and take first part as command name
        separator=" "
        parts = repr.split(separator, 1)

        #parse toggle and repeat indicattions
        if (parts[0].startswith(TOGGLE_STR)):
            self.Toggle = True
            self.Name = parts[0].replace(TOGGLE_STR,"")
        elif (parts[0].startswith(REPEAT_STR)):
            self.Repeat = True
            self.Name = parts[0].replace(REPEAT_STR,"")
        else:
            self.Name = parts[0]

        #parse text if present
        if (len(parts) > 1):
            #text is after any <> formats
            parts[1] = parts[1].replace("&gt;", ">")
            parts[1] = parts[1].replace("&lt;", "<")
            self.Text = parts[1].split(">")[-1]
            #parse formatting
            self.TextColor = ParseBracketedCodes(parts[1], COLOR_STR)
            self.TextBackgroundColor = ParseBracketedCodes(parts[1], BACKGROUND_STR)
            if (self.TextBackgroundColor.startswith("#") and (len(self.TextBackgroundColor) > len("#FFFFFF"))):
                #Transparency code present
                self.TextBackgroundTransparency = self.TextBackgroundColor[-2:]
                self.TextBackgroundColor = self.TextBackgroundColor[0:-2]
            self.TextBorderColor = ParseBracketedCodes(parts[1], BORDER_STR)
            self.TextScale = ParseBracketedCodes(parts[1], SCALE_STR)
            self.TextDuration = ParseBracketedCodes(parts[1], DURATION_STR)

    def GetTargetFile(self):
        if (self.IsLoadFileCommand()):
            return  os.path.abspath(RemoveOuterQuotes(self.Text))
        else:
            return None

    def SetTargetFile(self, path: str):
        self.Text = "\"" + path + "\""


    #Initialize with name and text or from a string representation
    #setting repr will override name and text
    def __init__(self, name: str = "", text: str = "", repeat: bool = False, toggle: bool = False, 
        color: str = "", background: str = "", transparency: str = "", border: str = "", scale: str = "", duration: str = "",
        repr: str = ""):

        #Name of the slash command.  See https://paragonwiki.com/wiki/List_of_Slash_Commands
        self.Name = ""

        #Text targeted by slash command such as the message for /say
        self.Text = ""

        #Command is set to repeat while clicked as in +forward for W
        self.Repeat = False

        #Command is set to repeat until clicked again is ++forward for R
        self.Toggle = False

        #color indicated by <color {ccode}> in text
        self.TextColor = ""

        #background color indicated by ccode in <bgcolor {ccode{transparency}>
        self.TextBackgroundColor = ""

        #background transparency indicated by transparency in <bgcolor {ccode{transparency}>
        self.TextBackgroundTransparency = ""

        #border color indicated by <bordercolor {code} in text>
        self.TextBorderColor = ""

        #scale indicated by <scale {factor}> in text
        self.TextScale = ""

        #text duration indicaated by <duration {seconds}> in text
        self.TextDuration = ""

        if (repr == ""):
            self.Name = name
            self.Text = text
            self.Repeat = repeat
            self.Toggle = toggle
            self.TextColor = color
            self.TextBackgroundColor = background
            self.TextBackgroundTransparency = transparency
            self.TextBorderColor = border
            self.TextScale = scale
            self.TextDuration = duration
        else:
            self.Parse(repr) 

    def IsLoadFileCommand(self)->bool:       

        #Indicates the command is loading a file
        return IsLoadFileCommand(self.Name)


    #Full command text with both text and format directions
    def FormattedText(self) -> str:
        text = self.Text

        #add formatting
        formatFormat = "<%s %s>"
        if (self.TextDuration != ""):
            text = formatFormat % (DURATION_STR, self.TextDuration) + text
        if (self.TextScale != ""):
            text = formatFormat % (SCALE_STR, self.TextScale) + text
        if (self.TextBorderColor != ""):
            text = formatFormat % (BORDER_STR, self.TextBorderColor) + text
        if (self.TextBackgroundColor != ""):
            color = self.TextBackgroundColor
            transparency = self.TextBackgroundTransparency 

            if ((not color.startswith("#")) and (str.strip(transparency) != "")):
                #named color with transparency
                try:
                    color = STANDARD_COLOR_DICTIONARY[self.TextBackgroundColor]
                except KeyError:
                    transparency = ""
            
            text = formatFormat % (BACKGROUND_STR, color + transparency) + text

        if (self.TextColor != ""):
            text = formatFormat % (COLOR_STR, self.TextColor) + text

        return text

    #command name with toggle or repeat formatting
    def FormattedName(self) -> str:
        result = self.Name
        #add toggle and repeat indicated before name
        if (self.Repeat):
            result = REPEAT_STR + result
        elif(self.Toggle):
            result = TOGGLE_STR + result
        return result      

    def __repr__(self):
        if (self.Text == ""):
            result = self.FormattedName()
        else:
            result = "%s %s" % (self.FormattedName(), self.FormattedText())
        return result

    def Clone(self):
        return SlashCommand(repr=self.__repr__())

def IsLoadFileCommand(command)-> bool:
    for loadFileCommand in LOAD_FILE_COMMANDS:
        if (CompareKeybindStrings(loadFileCommand, command)):
            return True
    return False


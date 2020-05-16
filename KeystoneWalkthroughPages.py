
import tkinter as tk
from KeystoneWizard import KeystoneWizard, KeystoneWizardPage
from KeystoneFormats import KeystoneFrame, KeystoneLabel
from KeystoneUtils import GetResourcePath
from PIL import ImageTk, Image
import webbrowser

WALKTHROUGH = [
    "Hi!  I'm Keystone.\n" +
    "You may remember me from hitting me in the face to get to Frostfire.\n" +
    "No hard feelings!\n"+
    "Now I'm becoming a 'reformed member of society'.\n\n" +
    "Jock asked me to help you get started with this software.\n" +
    "He says I help make speling n' grammer mistakes like its character.",

    'First lets get the keybinds for your favorite character!\n\n' +
    'From the Game Commands Menu select Download File.\n' + 
    'You will be prompted to select a save location and then a popup will appear\n' +
    "Click Next once you see it.  Don't click OK just yet!",

    "Like the window says, it has copied a game command to the clipboard.\n\n" +
    "Next you want to launch City of Heroes and log on the toon you want binds for.\n" +
    "Use ctrl-v to paste that command into the chat and hit enter.\n" +
    "You should see it say it saved the file to the path you chose.\n\n" +
    "I'll just wait patiently here while you do that.\n" +
    "Like I was doing in the office building before all the hitting...",

    "Welcome Back!\n\n" +
    "Now go ahead and click okay and it will open up the file you just saved.\n" +
    "If it worked you'll see a lot of lines of text in attractive 'lightskyblue'\n" +
    "Just like I'm talking in here.  We'll show how you can do that too.\n\n" +
    "The letter in front is the key.  Sometimes with a SHIFT or a CTRL\n" +
    "The 'Slash Commands' come next.  Maybe more that one joined with $$\n" +
    "This is all in the format the game uses.\n" +  
    "We're going to help you not need to know it so much\n\n" +
    "The little dots '...' are used to edit a bind.  Let's do that next.",

    "Everyone's Battle Cry could use a little color. We'll spruce yours up.\n" +
    "Look down the list for F10.  Probably say $battlecry $$ emote attack.\n" +
    "Click on the dots it and it will open up the editor in a new window.\n" +
    "Try that then click Next.",

    "Right, What we got here.  Says F10 at the top.\n" +
    "Also let's us know that the Key is F10 and this is an F key\n" +
    "You knew that.  Some will be less obvious.\n" +
    "Chord is for Shift, Ctrl, and Alt, but we don't have one here.\n\n" +
    "Ok for when your done. Cancel if you screw things up.\n\n" + 
    "Unbind lets us not tell the key anything in this file\n" +
    "...or tell it to do nothing, which is different if you follow...\n" +
    "...or assign it back to a default if we know one...\n" +
    "You can click it and then cancel to see what I mean\n\n" +
    "Then we have our two commands. Let's look at those next.",

    "Click on where it sez say.\n\n" +
    "We've got a bunch more buttons\n\n" +
    "That little red x next to Unbind lets us delete this command.\n" +
    "Not the key bind, just this one command.\n" +
    "The inserts and move would let us add more or rearrange things.\n" +
    "Try it out if you like.  We can always cancel\n" +
    "Thing is that first thing that make a toon more than jabber and emote\n" +
    "stops the whole list running.  So if you put multiple powers on one key,\n" +
    "then it will only do the first that works.\n\n" +
    "Our first command is say, which won't do that.\n" +
    "Let's look more closely at it.",

    
    "Down at the bottom it tells us what say does.\n" +
    "This is handy because there are like a hundred more if you open that list\n\n" +
    "To the right of say is the text for the command.\n" +
    "Some commands use text. Others don't. Hopefully the description will tell.\n\n" +
    "Repeat Mode could use a little explaining...",

    "Repeat mode is how often the command will run when you hit the key.\n" +
    "Once is ... well once.  Repeat does it for as long as you hold the key.\n" +
    "Toggle is over and over until you hit the key again.\n" +
    "So use the forward command 'Once' and you would have to keep tappin' W to move.\n" +
    "Repeat is forward while you hold W like normal\n" +
    "Toggle and you take off runnin' until you hit W again. See?\n" +
    "Don't toggle your battle cry.  Nobody wants that.",

    "Down at the bottom we can just switch to editing the command strings direct\n" +
    "This is handy to copy, and paste, or if you have been reading up on the commands,\n" +
    "and don't want the interface in your way for something clever like.\n\n" +
    "Below the text is all the stuff to make you talk pretty like me.\n" +
    "Let's look at that next.",

    "We have color.  You can pick from the list or use the color button to customize.\n" +
    "Pick something classy like 'lightskyblue'\n" +
    "It formats the text so we can see what we are getting. Cool huh?\n" +
    "...but now that pretty blue isn't readable.\n\n" +
    "Background color and border color work the same.  I like 'black'\n\n" +
    "Transparency is how see through the chat bubble will be\n" +
    "We used 'lightskyblue' again for the background to see through.\n" +
    "It really is a nice color\n\n" +
    "Scale makes for yelling big or whispering small.\n" +
    "It's a decimal from 0.1 tiny to 4.0 huge\n\n" +
    "Duration is how many seconds your wisdom will linger for.\n\n" +
    "Make things how you want and Ok it then click Next.",

    "Notice at the top we can save or cancel.\n" +
    "Cancel reloads the file if we want to undo our changes\n\n" +
    "Don't save just yet.  Let's add a new bind first.\n\n" +
    "Click the New Bind button.",

    "Here's the editing window again, but now you can assign the Key and the Chord.\n" +
    "Don't worry, it will warn you before it overwrites something.\n\n" +
    "It brought up the first Key on the list '1' and the default command for it.\n" +
    "Let's try something you are more likely to want to do!\n\n" +
    "Choose powexec_name from the command list.\n" +
    "This let's us use a power by name.  Me, I keep Hurl Boulder bound to the B key\n\n" +
    "Not that I will be hurling a boulder at you.\n"+
    "Because of the reform and everything.\n\n" +
    "Go on and add a bind if you want, and then I want to show you a special one next.",

    "Ready?  Go to the Game Command menu again and select Add Upload Bind.\n\n" +
    "There's the New Bind editor again, but its preloaded with an upload command.\n" +
    "Add this and we can use SHIFT+NUMPAD0 to reload the file when we edit it.\n" +
    "Or you can change the keys to whatever you want.\n\n" +
    "You might also want to change the text that lets you know it worked,\n" +
    "or you can delete it with the little red x next to it.\n\n" +
    "See the new and ... buttons next to the file name?\n" +
    "Those show up when you select bind_load_file or bind_load_file_silent.\n" +
    "That's so you can easily create chains of files.\n"
    "You can do cool tricks by having keys load files that bind other keys,\n" +
    "like having a key cycle through different powers each time you click it.\n" +
    "...but that's a whole other walkthrough.\n\n" +
    "Play around however you want with the file.\n" +
    "When you are ready, save or Save As from the File menu and let's upload these binds!",

    "Back in the Game Commands menu, select Upload File.\n\n" +
    "Just like the download it copied the command to the clipboard for you.\n" +
    "Go into City of Heroes and paste that in, and it will upload these binds,\n" +
    "and away you go!"
] 

WALKTHROUGH_END_PAGES = [
    ["Check out the guides we used to make this at:",
    [
    "http://www.dgath.com/coh/cohcovbmg200.pdf",
    "https://archive.paragonwiki.com/wiki/Slash_Commands",
    "https://cityofheroes.fandom.com/wiki/The_Incomplete_and_Unofficial_Guide_to_/bind"
    ]
    ],
    ["Complain and ask for features on GitHub:",
    ["https://github.com/Jock-Tamson/JocksKeystoneEditor"]
    ]
    ]

class KeystoneWalkthroughPages(KeystoneWizardPage):

    def __init__(self, wizard: KeystoneWizard, text: str, urls = None, *args, **kwargs):

        KeystoneWizardPage.__init__(self, wizard, allowBack = True, allowClose=True, allowNext=True, *args, **kwargs)

        self.columnconfigure(0, weight = 0)
        self.columnconfigure(1, weight = 1, minsize=510)
        self.rowconfigure(0, weight = 1)

        label = KeystoneLabel(self, text = text, wraplength=500, justify=tk.LEFT)
        label.grid(row=0, column=1, sticky='n', padx=5, pady=5 )

        imgPath = GetResourcePath('.\\Resources\\LeadBrick1.jpg')
        if (imgPath != None):
            self.Image = ImageTk.PhotoImage(Image.open(imgPath))
            imgPanel = tk.Label(self, image=self.Image)          
            imgPanel.grid(row=0, column=0, sticky='nsew')

        if (urls != None):
            urlFrame = KeystoneFrame(self)
            for idx, eachURL in enumerate(urls):
                link = KeystoneLabel(urlFrame, text = eachURL)
                link.bind("<Button-1>", lambda e, url = eachURL: self.callback(url))
                link.grid(row = idx, column=0, sticky='nsew')
            urlFrame.grid(row=0, column=1)

    def callback(self, url):
        webbrowser.open_new(url)


if (__name__ == "__main__"):

    win = tk.Tk()

    wizard = KeystoneWizard(win, title='Keystone Walkthrough')
    pages= []
    for eachLine in WALKTHROUGH:
        pages.append(KeystoneWalkthroughPages(wizard, text=eachLine))
    for text, urls in WALKTHROUGH_END_PAGES:
        pages.append(KeystoneWalkthroughPages(wizard, text=text, urls=urls))

    wizard.LoadPages(pages)

    tk.mainloop()

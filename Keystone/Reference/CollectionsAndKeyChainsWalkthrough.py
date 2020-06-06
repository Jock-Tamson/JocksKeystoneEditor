COLLECTIONS_AND_KEYCHAINS_WALKTHROUGH = [
"Back in the Intro Walkthrough I said there would be more on using bind_load_file.\n" +
"Well tell my parole board I am a man of my word, cuz here we go!\n"+
"\n" +
"If you haven't used Import and Exports yet you might want to do that first because\n"+
"I will use it here.",

"Having a key load another file let's you have that key change what it does,\n" +
"or what a bunch of other keys do too!\n" +
"\n"+
"We can use that to have a key cycle through different functions or to totally\n" +
"reconfigure your keyboard for different situations.  All at a key tap!\n"+
"\n"+
"One powerful example of this are Sandophan's Mastermind keybinds\n"+
"They are pinned to the top of the Mastermind forum for a good reason.\n" +
"We, uhmm, 'borrowed' them to include them in handy import files.\n" +
"\n" +
"Bring one in from the Predefined Binds in the Import Export menu and let's look.\n" +
"It will make you choose a path because there are multiple files linked to together.\n" +
"We need to know what path to use in the load commands.\n" +
"Won't save anything yet though.\n" +
"\n" +
"Import the Robotics one now.",

"Look at that. We grew a tree.\n" +
"\n" +
"In a process Jock described to me as 'Just hard enough to make him feel very stupid'\n" +
"it's found additional files that are loaded by binds and which key loads them.\n" +
"The little pencil icon. (Yes it is. You draw a tiny pencil!) shows what's new or edited.\n"
"\n" +
"Having a collection of files like this changes how the Save functions behave a little\n" +
"The save button in the file you are editing will still just save it.\n"+
"Save and Save As from the menu or the top will now save the entire collection.\n" +
"If you use Save As to change the path, it will even change all the load commands\n"
"so they are correct for their new home.\n" +
"\n" +
"Let's take a look at how these binds work",

"Scroll down and you will see we imported new binds for the numpad 0 to 3 keys.\n" +
"Each one loads a different file, and we can see those 4 files in the tree.\n" +
"Numpad 0 now loads a file called all.txt.\n" +
"\n" +
"Click on it on the tree to see what it does.",

"all.txt is binding the numpad 4 to 9 keys to control all the pets.\n" +
"Handy, but not using the full power of our fully armed and operational robots.\n" +
"Numpad 1 now loads a file called BattleDrones.txt.  Click on that file in the tree.\n" +
"\n" +
"BattleDrones.txt binds the same 6 numpad keys, but now they control the Drones\n" +
"Numpad 0 - Numpad 4.  Everyone runs over to assault some mostly innocent Outcast.\n" +
"Numpad 1 - Numpad 5.  Just the Battle Drones rush back to protect you.  Cool yeah?\n" +
"\n" +
"Folks use this same technique to reconfigure for flight or teleport.\n" +
"Heck if more than 3 people ever read this someone might have provided a kst file\n" +
"\n" +
"This is just one layer though.  What if the files we loaded, loaded files?\n" +
"We've provided an example.",

"Go back to your top file and import jump_chain.kst from the Predefined binds.\n" +
"Now we've got 2 files on the middle mouse button.  How does that work?\n" +
"\n" +
"The bind in your top file is starting Combat Jumping and loading MBUTTON2.txt.\n" +
"\n" +
"If you look at MBUTTON2.txt, it binds the same button to Super Jump, the it loads\n" +
"MBUTTON1.txt.\n" +
"\n" +
"MBUTTON1.txt.  MBUTTON1.txt is Combat Jumping again, and it loads MBUTTON2.txt\n" +
"So MBUTTON1 loads MBUTTON2 loads MBUTTON1 and so on.  Wait why?\n" +
"\n" +
"Well now I toggle between Combat Jumping and Super Leap each time I click the button.\n" +
"\n" +
"As long as you close the loop back to the first file you loaded in the top file,\n" +
"you could chain any number of files together like this.\n" +
"You could deliver the entire Gettysburgh Address in a series on the G key,\n" +
"or have 15 different snarky comments to cycle every time you use a rez power.\n" +
"\n" +
"You can get started just by adding a bind_load_file_silent command to a file.\n" +
"The tree will appear and you can start to chain things together."
]

COLLECTIONS_AND_KEYCHAINS_WALKTHROUGH_END_PAGES = [
    ["More on Sandophan's binds and making rotating binds:",
    [
    "https://forums.homecomingservers.com/topic/6500-the-homecoming-of-sandolphans-mm-numpad-binds/",
    "https://archive.paragonwiki.com/wiki/Slash_Commands",
    "https://cityofheroes.fandom.com/wiki/The_Incomplete_and_Unofficial_Guide_to_/bind"
    ]
    ],
    ["Correct spelling and add a predefined bind for the Gettysburg Address on GitHub:",
    ["https://github.com/Jock-Tamson/JocksKeystoneEditor"]
    ]
    ]

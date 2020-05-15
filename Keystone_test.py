from SlashCommand import SlashCommand 
from Bind import Bind
from BindFile import BindFile
from BindFile import ReadBindsFromFile
from BindFile import GetDefaultBindForKey
from KeystoneUtils import ParseBracketedCodes, AverageRGBValues, GetFileName, GetUniqueFilePath, ReverseDictionaryLookup, RemoveOuterQuotes
from BindFileCollection import BindFileCollection
from BindFileCollection import GetKeyChains
from Keylink import Keylink
from Keychain import Keychain

from os import remove
from os import path
import os

import unittest

class TestKeystoneUtils(unittest.TestCase):

    def test_ParseBacketedCodes(self):
        input = "<color #000000><bgcolor #FFFFFF75> <bordercolor #FF0000><scale 1.0><duration 10>"
        tests = [
                    ["color", "#000000"],
                    ["bgcolor", "#FFFFFF75"],
                    ["bordercolor", "#FF0000"],
                    ["scale", "1.0"],
                    ["duration", "10"]
                ]
        for test in tests:
            actual = ParseBracketedCodes(input, test[0])
            expected = test[1]
            self.assertEqual(actual, expected)

    def test_AverageRGBValues(self):
        val1 = "#FFFFFF"
        val2 = "#000000"
        expected = "#7F7F7F"
        actual = AverageRGBValues(val1, val2)
        self.assertEqual(actual, expected, "Values with #")
        val1 = "white"
        actual = AverageRGBValues(val1, val2)
        self.assertEqual(actual, expected, "Values with names")
        val1 = "red"
        val2 = "lightskyblue"
        avg = 80
        expected = "#9FA4C8"
        actual = AverageRGBValues(val1, val2, avg)
        self.assertEqual(actual, expected, "Using average")

    def test_GetFileName(self):
        actual = GetFileName(".\\TestReferences\\Jock Tamson\\MouseChord2.txt")
        expected = "MouseChord2.txt"
        self.assertEqual(actual, expected)

    def test_GetUniqueFilePath(self):
        filePath = ".\\TestReferences\\Jock Tamson\\MouseChord2.txt" 
        actual = GetUniqueFilePath(filePath)
        expected = os.path.abspath(".\\TestReferences\\Jock Tamson\\MouseChord2(1).txt")
        self.assertEqual(actual, expected)
        #test with seed
        actual = GetUniqueFilePath(filePath, 5)
        expected = os.path.abspath(".\\TestReferences\\Jock Tamson\\MouseChord2(5).txt")
        self.assertEqual(actual, expected)
        #test non paranthetical
        actual = GetUniqueFilePath(filePath=filePath, paranthetical=False)
        expected = os.path.abspath(".\\TestReferences\\Jock Tamson\\MouseChord21.txt")
        self.assertEqual(actual, expected)
        #test used names
        usedNames = ["MouseChord2(1).txt", "MouseChord2(2).txt"]
        actual = GetUniqueFilePath(filePath=filePath, usedNames=usedNames)
        expected = os.path.abspath(".\\TestReferences\\Jock Tamson\\MouseChord2(3).txt")

    def test_ReverseDictionaryLookup(self):
        target = {"one" : 1, "two" : 2, "three" : 3}
        expected = "two"
        actual = ReverseDictionaryLookup(target, 2)
        self.assertEqual(actual, expected)

class TestSlashCommand(unittest.TestCase):

    def test__repr__(self):
        name = "say"
        text = "This test passed"
        expected = "say This test passed"
        target = SlashCommand(name=name, text=text)
        actual = str(target)
        self.assertEqual(actual, expected)

        #toggle command with no text
        name = "forward"
        text = ""
        toggle = True
        expected = "++forward"
        target = SlashCommand(name=name, text=text, toggle=toggle)
        actual = str(target)
        self.assertEqual(actual, expected)

        #repeat command with no text
        name = "forward"
        text = ""
        repeat = True
        expected = "+forward"
        target = SlashCommand(name=name, text=text, repeat=repeat)
        actual = str(target)
        self.assertEqual(actual, expected)

        #formatted text
        name = "say"
        text = "Yay!"
        color = "#000000"
        background = "#FFFFFF"
        transparency = "75"
        border = "#FF0000"
        scale = "1.0"
        duration = "10"
        target = SlashCommand(name=name, text=text, color=color, background=background, transparency=transparency, border=border, scale=scale, duration=duration)
        actual = str(target)
        expected = "say <color #000000><bgcolor #FFFFFF75><bordercolor #FF0000><scale 1.0><duration 10>Yay!"
        self.assertEqual(actual, expected)

    def test_FromString(self):
        target = SlashCommand(repr="say This test passed")
        expected = "say"
        actual = target.Name
        self.assertEqual(actual, expected, "Parse name")
        expected = "This test passed"
        actual = target.Text
        self.assertEqual(actual, expected, "Parse text")

        #command with no text
        target = SlashCommand(repr="menu")
        expected = "menu"
        actual = target.Name
        self.assertEqual(actual, expected, "Parse name with no text")
        expected = ""
        actual = target.Text
        self.assertEqual(actual, expected, "Parse no text")

        #preserve quotes on path
        target = SlashCommand(repr="bind_load_file \"C:\\Program Files\"")
        expected = "\"C:\\Program Files\""
        actual = target.Text
        self.assertEqual(actual, expected, "Preserve quotes on a path")

        #parse repeat command
        target = SlashCommand(repr="+forward")
        self.assertEqual(target.Repeat, True, "Did not set Repeat as expected")
        self.assertEqual(target.Name, "forward", "Did not parse repeat command name as expected")

        #parse toggle command
        target = SlashCommand(repr="++forward")
        self.assertEqual(target.Toggle, True, "Did not set Toggle as expected")
        self.assertEqual(target.Name, "forward", "Did not parse toggle command name as expected")

        #formatted text
        name = "say"
        text = "Yay!"
        color = "#000000"
        background = "#FFFFFF"
        transparency = "75"
        border = "#FF0000"
        scale = "1.0"
        duration = "10"
        target = SlashCommand(repr="say <color #000000><bgcolor #FFFFFF75><bordercolor #FF0000><scale 1.0><duration 10>Yay!")
        self.assertEqual(target.Name, name, "Did not parse name from formatting as expected")
        self.assertEqual(target.Text, text, "Did not parse text from formatting as expected")
        self.assertEqual(target.TextColor, color, "Did not parse color from formatting as expected")
        self.assertEqual(target.TextBackgroundColor, background, "Did not parse background from formatting as expected")
        self.assertEqual(target.TextBackgroundTransparency, transparency, "Did not parse transparency from formatting as expected")
        self.assertEqual(target.TextBorderColor, border, "Did not parse border from formatting as expected")
        self.assertEqual(target.TextScale, scale, "Did not parse scale from formatting as expected")
        self.assertEqual(target.TextDuration, duration, "Did not parse duration from formatting as expected")

        #formatted text with &gt; &lt;
        target = SlashCommand(repr="local &lt;color white&gt;&lt;bgcolor #2222aa&gt;&lt;scale .75&gt;level $level $archetype")
        name = "local"
        text = "level $level $archetype"
        color = "white"
        background = "#2222aa"
        scale = ".75"
        self.assertEqual(target.Name, name, "Did not parse name from formatting as expected")
        self.assertEqual(target.Text, text, "Did not parse text from formatting as expected")
        self.assertEqual(target.TextColor, color, "Did not parse color from formatting as expected")
        self.assertEqual(target.TextBackgroundColor, background, "Did not parse background from formatting as expected")
        self.assertEqual(target.TextScale, scale, "Did not parse scale from formatting as expected")

    def test_TargetFile(self):

        target = SlashCommand(repr="say This test passed")
        self.assertEqual(target.IsLoadFileCommand(), False, "Unexpectedly set IsLoadFileCommand")
        self.assertEqual(target.GetTargetFile(), None, "Unexpectedly set TargetFile")
        target = SlashCommand(repr="bind_load_file \".\\TestReferences\\Jock Tamson\\MouseChord2.txt\"")
        self.assertEqual(target.IsLoadFileCommand(), True, "Unexpectedly did not set IsLoadFileCommand")
        target = SlashCommand(repr="bind_load_file_silent \".\\TestReferences\\Jock Tamson\\MouseChord2.txt\"")
        self.assertEqual(target.IsLoadFileCommand(), True, "Unexpectedly did not set silent IsLoadFileCommand") 
        self.assertEqual(target.GetTargetFile(), os.path.abspath(".\\TestReferences\\Jock Tamson\\MouseChord2.txt"), "Did not get expected TargetFile")
        target.SetTargetFile(".\\NewPath\\Jock Tamson\\MouseChord2.txt")
        self.assertEqual(target.GetTargetFile(), os.path.abspath(".\\NewPath\\Jock Tamson\\MouseChord2.txt"), "Did not set expected TargetFile")

class TestBind(unittest.TestCase):

    def test__repr__(self):
        #test a single command
        key = "A"
        commands = [SlashCommand(name="say", text="This test passed")]
        expected = "A \"say This test passed\""
        target = Bind(key=key, commands=commands)
        actual = str(target)
        self.assertEqual(actual, expected, "Single command")

        #test concatenated commands
        commands = [SlashCommand(name="say", text="This test passed"), SlashCommand(name="emote", text="Yay!")]
        expected = "A \"say This test passed$$emote Yay!\""
        target = Bind(key=key, commands=commands)
        actual = str(target)
        self.assertEqual(actual, expected, "Multiple commands")

        #test chord
        key = "A"
        chord = "CTRL"
        commands = [SlashCommand(name="say", text="This test passed")]
        expected = "CTRL+A \"say This test passed\""
        target = Bind(key=key, chord=chord, commands=commands)
        actual = str(target)
        self.assertEqual(actual, expected, "Chord in key")

    def test_FromString(self):
        #test single command bound to key (with leading spaces)
        target = Bind(repr = "   A \"say This test passed\"")
        self.assertEqual(target.Key, "A", "Did not find expected KeyName on a single command")
        actual = len(target.Commands)
        self.assertEqual(actual, 1, "Did not find expected command count on a single command")
        actual = target.Commands[0].Name
        self.assertEqual(actual, "say", "Did not find expected command name on a single command")
        actual = target.Commands[0].Text
        self.assertEqual(actual, "This test passed", "Did not find expected command text on a single command")

        #test concatenated commands bound to a key
        target = Bind(repr = "A \"say This test passed $$ emote Yay!\"")
        self.assertEqual(target.Key, "A", "Did not find expected KeyName on concatenated commands")
        actual = len(target.Commands)
        self.assertEqual(actual, 2, "Did not find expected command count on concatenated commands")
        actual = target.Commands[0].Name
        self.assertEqual(actual, "say", "Did not find expected 1st command name on concatenated commands")
        actual = target.Commands[0].Text
        self.assertEqual(actual, "This test passed ", "Did not find expected 1st command text on concatenated commands")
        actual = target.Commands[1].Name
        self.assertEqual(actual, "emote", "Did not find expected 2nd command name on concatenated commands")
        actual = target.Commands[1].Text
        self.assertEqual(actual, "Yay!", "Did not find expected 2nd command text on concatenated commands")

        #test string with quote bound space
        expected ="COMMA \"show chat$$beginchat /tell $target, \""
        target = Bind(repr = "COMMA \"show chat$$beginchat /tell $target, \"")
        actual = str(target)
        self.assertEqual(actual, expected, "Did not get expected round trip on a Bind with a space bound by quotes")

        #test key with a chord
        target = Bind(repr = "SHIFT+A \"say This test passed\"")
        self.assertEqual(target.Key, "A", "Did not find expected KeyName on a chord")
        self.assertEqual(target.Chord, "SHIFT", "Did not find expected Chord on a chord")
        actual = len(target.Commands)
        self.assertEqual(actual, 1, "Did not find expected command count on a chord")
        actual = target.Commands[0].Name
        self.assertEqual(actual, "say", "Did not find expected command name on a chord")
        actual = target.Commands[0].Text
        self.assertEqual(actual, "This test passed", "Did not find expected command text on a chord")

        #test load file bind
        self.assertEqual(target.IsLoadFileBind(), False, "Unexpectedly set IsLoadFileBind")
        target = Bind(repr = "MouseChord \"powexec_name Hover$$bind_load_file \".\\TestReferences\\Jock Tamson\\MouseChord2.txt\"\"")
        self.assertEqual(target.IsLoadFileBind(), True, "Unexpectedly did not set IsLoadFileBind")

class TestBindFile(unittest.TestCase):

    def test__repr__(self):
        expected = "A \"say This test passed\"\nB \"emote Yay!\""
        binds = [Bind(key="A", commands=[SlashCommand("say", "This test passed")]), Bind(key="B", commands=[SlashCommand("emote", "Yay!")])]
        target = BindFile(binds)
        actual = str(target)
        self.assertEqual(actual, expected)

    def test_FromString(self):
        input = "A \"say This test passed\"\nB \"emote Yay!\""
        target = BindFile(repr=input)
        actual = len(target.Binds)
        self.assertEqual(actual, 2, "Did not find expected bind count")
        actual = str(target.Binds[0])
        expected = str(Bind(key="A", commands=[SlashCommand("say","This test passed")]))
        self.assertEqual(actual, expected, "Did not find expected 1st bind")
        actual = str(target.Binds[1])
        expected = str(Bind(key="B", commands=[SlashCommand("emote","Yay!")]))
        self.assertEqual(actual, expected, "Did not find expected 2nd bind")

    def test_LoadFromFile(self):
        refFilePath = "./TestReferences/keybinds.txt"
        target = ReadBindsFromFile(refFilePath)
        f = open(refFilePath)
        try:
            expected = f.read()
        finally:
            f.close()
        self.assertEqual(target.FilePath, refFilePath, "Did not set expected filePath")
        actual = str(target)
        expectedParts = expected.splitlines()
        actualParts = actual.splitlines()
        for idx, expectedPart in enumerate(expectedParts):
            actualPart = actualParts[idx]
            self.assertEqual(actualPart, expectedPart, "Mismatch on line %d" % (idx+1))

    def test_RepointPaths(self):

        def _compareResults():    
            for idx, bind in enumerate(target.GetLoadFileBinds()):
                for command in bind.GetLoadFileCommands():
                    actual = command.GetTargetFile()
                    self.assertEqual(actual, expected[idx], "Did not find expected path for idx " + str(idx))

        refFilePath = "./TestReferences/Field Test/keybinds.txt"
        target = ReadBindsFromFile(refFilePath)
        target.RepointFilePaths("./NewPath/Field Test/keybinds.txt")
        expected =  [os.path.abspath(p) for p in ["./NewPath/Field Test/I1.txt", "./NewPath/Field Test/MBUTTON1.txt", "./NewPath/Field Test/keybinds.txt", "./TestReferences/keybinds(1).txt"]]
        _compareResults()
        target = ReadBindsFromFile(refFilePath)
        target.RepointFilePaths("./TestReferences/Field Test/new_keybinds.txt")
        expected =  [os.path.abspath(p) for p in ["./TestReferences/Field Test/I1(1).txt", "./TestReferences/Field Test/MBUTTON1(1).txt", "./TestReferences/Field Test/new_keybinds.txt", "./TestReferences/keybinds(1).txt"]]
        _compareResults()

    def test_WriteToFile(self):
        input = "A \"say This test passed\"\nB \"emote Yay!\""
        filePath = "./TestReferences/out.txt" 
        if (path.exists(filePath)):
            remove(filePath)
        target = BindFile(repr=input)
        self.assertEqual(target.FilePath, None, "FilePath set when loading from repr only")
        target.WriteBindsToFile(filePath)
        self.assertEqual(target.FilePath, filePath, "Did not set expected filePath")
        assert(path.exists(filePath))
        file = open(filePath)
        try:
            actual = file.read()
        finally:
            file.close() 
            remove(filePath)
        self.assertEqual(actual, input)

        filePath = "./TestReferences/NewDir/SubDir/out.txt" 
        target.WriteBindsToFile(filePath)
        self.assertEqual(target.FilePath, filePath, "Did not set expected filePath")
        assert(path.exists(filePath))
        file = open(filePath)
        try:
            actual = file.read()
        finally:
            file.close() 
            remove(filePath)
            os.removedirs("./TestReferences/NewDir/SubDir")
        self.assertEqual(actual, input)

    def test_GetBindForKey(self):
        expected_2 = "2 \"powexec_slot 2\""
        expected_CTRL_2 = "CTRL+2 \"powexec_alt2slot 2\""
        expected_SHIFT_2 = "SHIFT+2 \"team_select 2\""
        input = "%s\n%s\n%s\n" % (expected_2, expected_CTRL_2, expected_SHIFT_2)
        target = BindFile(repr=input)
        actual = target.GetBindForKey(key = "2")
        self.assertEqual(1, len(actual))
        self.assertEqual(expected_2, str(actual[0]))
        actual = target.GetBindForKey(key = "2", chord="CTRL")
        self.assertEqual(1, len(actual))
        self.assertEqual(expected_CTRL_2, str(actual[0]))
        actual = target.GetBindForKey(key = "2", chord="SHIFT")
        self.assertEqual(1, len(actual))
        self.assertEqual(expected_SHIFT_2, str(actual[0]))
        actual = target.GetBindForKey(key = "A")
        self.assertEqual(0, len(actual))

    def test_GetDefaultBindForKey(self):
        expected_2 = "2 \"powexec_slot 2\""
        expected_SHIFT_2 = "SHIFT+2 \"team_select 2\""
        expected_SHIFT_F1 = "SHIFT+F1 \"nop\""
        actual = str(GetDefaultBindForKey(key="2"))
        self.assertEqual(expected_2, actual)
        actual = str(GetDefaultBindForKey(key="2", chord="SHIFT"))
        self.assertEqual(expected_SHIFT_2, actual)
        actual = str(GetDefaultBindForKey(key="F1", chord="SHIFT"))
        self.assertEqual(expected_SHIFT_F1, actual)


class TestBindFileCollection(unittest.TestCase):

    def test_GetBoundPaths(self):
        path = ".\\TestReferences\\Field Test\\keybinds.txt"
        target = ReadBindsFromFile(path)
        actual = {}
        GetKeyChains(target, path, actual)
        self.assertEqual(len(actual), 3)
        self.assertEqual(len(actual["I"]), 2)
        self.assertEqual(len(actual["MBUTTON"]), 2)
        self.assertEqual(len(actual["SHIFT+NUMPAD0"]), 1)

    def test_NoBoundPaths(self):
        path = ".\\TestReferences\\Soda Juice\\keybinds.txt"
        target = ReadBindsFromFile(path)
        actual = {}
        GetKeyChains(target, path, actual)
        self.assertEqual(len(actual), 0)

    def test_Load(self):
        target = BindFileCollection(".\\TestReferences\\Field Test\\keybinds.txt")
        self.assertEqual(len(target.KeyChains), 3)
        self.assertEqual(len(target.KeyChains["I"]), 2)
        self.assertEqual(len(target.KeyChains["MBUTTON"]), 2)
        self.assertEqual(len(target.KeyChains["SHIFT+NUMPAD0"]), 1)

    def test_NonCircularChain(self):
        target = BindFileCollection(".\\TestReferences\\Jock Tamson\\keybinds.txt")
        self.assertEqual(len(target.KeyChains), 2)
        self.assertEqual(len(target.KeyChains["MBUTTON"]), 2)
        self.assertEqual(len(target.KeyChains["MouseChord"]), 4)

    def test_RepointBindFileCollection(self):

        def _compare():
            idx = 0
            for bind in target.File.GetLoadFileBinds():
                for command in bind.GetLoadFileCommands():
                    actual = command.GetTargetFile()
                    self.assertEqual(actual, expected[idx], "Did not find expected path for idx " + str(idx))
                    idx = idx + 1
            for bindFile in target.GetBoundFiles():
                for bind in bindFile.GetLoadFileBinds():
                    for command in bind.GetLoadFileCommands():
                        actual = command.GetTargetFile()
                        self.assertEqual(actual, expected[idx], "Did not find expected path for idx " + str(idx))
                        idx = idx + 1

        target = BindFileCollection(".\\TestReferences\\Field Test\\keybinds.txt")
        target.RepointFilePaths(".\\NewPath\\Field Test\\keybinds.txt")
        expected =  [os.path.abspath(p) for p in [
            "./NewPath/Field Test/I1.txt", 
            "./NewPath/Field Test/MBUTTON1.txt", 
            "./NewPath/Field Test/keybinds.txt", 
            "./TestReferences/keybinds(1).txt",
            "./NewPath/Field Test/I2.txt",
            "./NewPath/Field Test/I1.txt", 
            "./NewPath/Field Test/MBUTTON2.txt", 
            "./NewPath/Field Test/MBUTTON1.txt"]]
        _compare()
        
        target = BindFileCollection(".\\TestReferences\\Field Test\\keybinds.txt")
        target.RepointFilePaths(".\\TestReferences\\Field Test\\new_keybinds.txt")
        expected =  [os.path.abspath(p) for p in [
            "./TestReferences/Field Test/I1(1).txt", 
            "./TestReferences/Field Test/MBUTTON1(1).txt", 
            "./TestReferences/Field Test/new_keybinds.txt", 
            "./TestReferences/keybinds(1).txt",
            "./TestReferences/Field Test/I2(1).txt",
            "./TestReferences/Field Test/I1(1).txt", 
            "./TestReferences/Field Test/MBUTTON2(1).txt", 
            "./TestReferences/Field Test/MBUTTON1(1).txt"]]
        _compare()

    def test_New(self):
        target = BindFileCollection()
        target.New()
        self.assertEqual(1, len(target.File.Binds), "Unexpected empty bind length")
        self.assertEqual("1", target.File.Binds[0].Key, "Unexpected empty key")
        self.assertEqual("powexec_slot", target.File.Binds[0].Commands[0].Name, "Unexpected empty command")
        self.assertEqual("1", target.File.Binds[0].Commands[0].Text, "Unexpected empty command text")
        target.New(defaults=True)
        self.assertEqual(104, len(target.File.Binds), "Unexpected default bind length")
        self.assertEqual("'", target.File.Binds[0].Key, "Unexpected default key")
        self.assertEqual("quickchat", target.File.Binds[0].Commands[0].Name, "Unexpected default command")
        self.assertEqual("", target.File.Binds[0].Commands[0].Text, "Unexpected default command text")

class TestKeylink(unittest.TestCase):

    def test_init(self):
        refFilePath = "./TestReferences/Field Test/I1.txt"
        bindFile = ReadBindsFromFile(refFilePath)
        target = Keylink(key="I", chord="", bindFile=bindFile)
        actual = target.FilePath
        expected = os.path.abspath(refFilePath)
        self.assertEqual(actual, expected, "Unexpected FilePath")
        actual = target.Key
        expected = "I"
        self.assertEqual(actual, expected, "Unexpected Key")
        actual = target.Chord
        expected = ""
        self.assertEqual(actual, expected, "Unexpected Chord")
        actual = target.Bind.__repr__()
        expected = "I \"powexec_name Radiation Infection$$bind_load_file \".\\TestReferences\\Field Test\\I2.txt\"\""
        self.assertEqual(actual, expected, "Unexptected Bind")
        actual = target.Command.__repr__()
        expected = "bind_load_file \".\\TestReferences\\Field Test\\I2.txt\""
        self.assertEqual(actual, expected, "Unexpected Command")
        actual = target.TargetFilePath
        expected = os.path.abspath("./TestReferences/Field Test/I2.txt")
        self.assertEqual(actual, expected, "Unexpected TargetFilePath")

    def test_ChangeKey(self):
        refFilePath = "./TestReferences/Field Test/I1.txt"
        bindFile = ReadBindsFromFile(refFilePath)
        target = Keylink(key="I", chord="", bindFile=bindFile)
        actual = target.Key
        expected = "I"
        self.assertEqual(actual, expected, "Unexpected Key")
        expected = "J"
        target.ChangeKey(expected)
        actual = target.Key
        self.assertEqual(actual, expected, "Unexpected changed Key")
        actual = target.Bind.Key
        self.assertEqual(actual, expected, "Unexpected changed Key in Bind")

    def test_ChangeChord(self):
        refFilePath = "./TestReferences/Field Test/I1.txt"
        bindFile = ReadBindsFromFile(refFilePath)
        target = Keylink(key="I", chord="", bindFile=bindFile)
        actual = target.Chord
        expected = ""
        self.assertEqual(actual, expected, "Unexpected Chord")
        expected = "SHIFT"
        target.ChangeChord(expected)
        actual = target.Chord
        self.assertEqual(actual, expected, "Unexpected changed Chord")
        actual = target.Bind.Chord
        self.assertEqual(actual, expected, "Unexpected changed Chord in Bind")

    def test_ChangeTargetFilePath(self):
        refFilePath = "./TestReferences/Field Test/I1.txt"
        bindFile = ReadBindsFromFile(refFilePath)
        target = Keylink(key="I", chord="", bindFile=bindFile)
        actual = target.TargetFilePath
        expected = os.path.abspath("./TestReferences/Field Test/I2.txt")
        self.assertEqual(actual, expected, "Unexpected TargetFilePath")
        expected = os.path.abspath("./TestReferences/Field Test/Toggles/I2.txt")
        target.ChangeTargetFilePath(expected)
        actual = target.TargetFilePath
        self.assertEqual(actual, expected, "Unexpected changed TargetFilePath")
        actual = RemoveOuterQuotes(target.Command.Text)
        self.assertEqual(actual, expected, "Unexpected changed TargetFilePath in Command")
        
class TestKeychain(unittest.TestCase):

    def test_init(self):
        refFilePath = "./TestReferences/Field Test/keybinds.txt"
        collection = BindFileCollection(refFilePath)
        target = Keychain(collection, "I")
        actual = target.Key
        expected = "I"
        self.assertEqual(actual, expected, "Unexpected Key")
        actual = target.Chord
        expected = ""
        self.assertEqual(actual, expected, "Unexpected Chord")
        actual = len(target.Links)
        expected = 2
        self.assertEqual(actual, expected, "Unexpected Links length")
        actual = target.Links[1].TargetFilePath
        expected = target.Links[0].FilePath
        self.assertEqual(actual, expected, "Unexpected file paths")
        actual = target.Anchor.FilePath
        expected = os.path.abspath(refFilePath)
        self.assertEqual(actual, expected, "Unexpected anchor file path")

    def test_ChangeKey(self):
        refFilePath = "./TestReferences/Field Test/keybinds.txt"
        collection = BindFileCollection(refFilePath)
        target = Keychain(collection, "I")
        actual = target.Key
        expected = "I"
        self.assertEqual(actual, expected, "Unexpected Key")
        expected = "J"
        target.ChangeKey(expected)
        actual = target.Key
        self.assertEqual(actual, expected, "Unexpected changed Key")
        actual = target.Anchor.Key
        self.assertEqual(actual, expected, "Unexpected changed Key in anchor")
        for idx, link in enumerate(target.Links):
            actual = link.Key
            self.assertEqual(actual, expected, "Unexpected changed Key in Link " + str(idx))
        self.assertTrue("J" in collection.KeyChains)
        self.assertFalse("I" in collection.KeyChains)

    def test_ChangeChord(self):
        refFilePath = "./TestReferences/Field Test/keybinds.txt"
        collection = BindFileCollection(refFilePath)
        target = Keychain(collection, "I")
        actual = target.Chord
        expected = ""
        self.assertEqual(actual, expected, "Unexpected Chord")
        expected = "SHIFT"
        target.ChangeChord(expected)
        actual = target.Chord
        self.assertEqual(actual, expected, "Unexpected changed Chord")
        actual = target.Anchor.Chord
        self.assertEqual(actual, expected, "Unexpected changed Chord in anchor")
        for idx, link in enumerate(target.Links):
            actual = link.Chord
            self.assertEqual(actual, expected, "Unexpected changed Chord in Link " + str(idx))
        self.assertTrue("SHIFT+I" in collection.KeyChains)
        self.assertFalse("I" in collection.KeyChains)

    def test_NewLink(self):
        refFilePath = "./TestReferences/Field Test/keybinds.txt"
        collection = BindFileCollection(refFilePath)
        chain = Keychain(collection, "I")
        newFilePath = "./TestReferences/Field Test/I3.txt"
        target = chain.Newlink(newFilePath)
        actual = target.FilePath
        expectedPath = os.path.abspath(newFilePath)
        self.assertEqual(actual, expectedPath, "Unexpected FilePath")
        actual = target.Key
        expected = "I"
        self.assertEqual(actual, expected, "Unexpected Key")
        actual = target.Chord
        expected = ""
        self.assertEqual(actual, expected, "Unexpected Chord")
        actual = target.Bind.__repr__()
        expected = "I \"bind_load_file \"%s\"\"" % expectedPath
        self.assertEqual(actual, expected, "Unexptected Bind")
        actual = target.Command.__repr__()
        expected = "bind_load_file \"%s\"" % expectedPath
        self.assertEqual(actual, expected, "Unexpected Command")
        actual = target.TargetFilePath
        self.assertEqual(actual, expectedPath, "Unexpected TargetFilePath")

    def test_Relink(self):

        def _testLinks():
            for idx, testCase in enumerate(expected):
                expectedFilePath = os.path.abspath(testCase[0])
                expectedTargetFilePath = os.path.abspath(testCase[1])
                actualFilePath = target.Links[idx].FilePath
                actualTargetFilePath = target.Links[idx].TargetFilePath
                self.assertEqual(actualFilePath, expectedFilePath, "Unexpected FilePath in link " + str(idx))
                self.assertEqual(actualTargetFilePath, expectedTargetFilePath, "Unexpected TargetFilePath in link " + str(idx))

        refFilePath = "./TestReferences/Field Test/keybinds.txt"
        collection = BindFileCollection(refFilePath)
        target = Keychain(collection, "I")
        newFilePath = "./TestReferences/Field Test/I3.txt"
        newLink = target.Newlink(newFilePath)
        target.Links.insert(1, newLink)
        target.Relink()
        expectedTargetFilePath = os.path.abspath("./TestReferences/Field Test/I1.txt")
        actualTargetFilePath = target.Anchor.TargetFilePath
        self.assertEqual(actualTargetFilePath, expectedTargetFilePath)
        expected = (
            ("./TestReferences/Field Test/I1.txt", "./TestReferences/Field Test/I3.txt"),
            ("./TestReferences/Field Test/I3.txt", "./TestReferences/Field Test/I2.txt"),
            ("./TestReferences/Field Test/I2.txt", "./TestReferences/Field Test/I1.txt")
        )
        _testLinks()
        
        newFilePath = "./TestReferences/Field Test/I4.txt"
        newLink = target.Newlink(newFilePath)
        target.Links.insert(0, newLink)
        target.Relink()
        expectedTargetFilePath = os.path.abspath("./TestReferences/Field Test/I4.txt")
        actualTargetFilePath = target.Anchor.TargetFilePath
        self.assertEqual(actualTargetFilePath, expectedTargetFilePath)
        expected = (
            ("./TestReferences/Field Test/I4.txt", "./TestReferences/Field Test/I1.txt"),
            ("./TestReferences/Field Test/I1.txt", "./TestReferences/Field Test/I3.txt"),
            ("./TestReferences/Field Test/I3.txt", "./TestReferences/Field Test/I2.txt"),
            ("./TestReferences/Field Test/I2.txt", "./TestReferences/Field Test/I4.txt")
        )
        _testLinks()

    def test_GetNewFileName(self):
        refFilePath = "./TestReferences/Field Test/keybinds.txt"
        collection = BindFileCollection(refFilePath)
        target = Keychain(collection, "I")
        actual = target.GetNewFileName()
        expected = os.path.abspath("./TestReferences/Field Test/I3.txt")
        self.assertEqual(actual, expected)

if __name__ == "__main__":
    unittest.main()
import os
import unittest
from os import path, remove

from Keystone.Model.Bind import Bind
from Keystone.Model.BindFile import (BindFile, GetDefaultBindForKey,
                                     ReadBindsFromFile)
from Keystone.Model.BindFileCollection import BindFileCollection, GetKeyChains
from Keystone.Model.Keychain import Keychain
from Keystone.Model.SlashCommand import SlashCommand
from Keystone.Reference.KeyNames import CHORD_KEYS, KEY_NAMES
from Keystone.Utility.KeystoneUtils import (AverageRGBValues, GetFileName,
                                            GetUniqueFilePath, MatchKeyName,
                                            ParseBracketedCodes,
                                            RemoveOuterQuotes,
                                            ReverseDictionaryLookup)


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

    def test_MatchKeyName(self):

        #match key
        target = ';'
        expected = (';','SEMICOLON','')
        actual = MatchKeyName(target, KEY_NAMES)
        self.assertEqual(actual, expected, 'Failed to match ;')

        #match alt key name
        target = 'SEMICOLON'
        actual = MatchKeyName(target, KEY_NAMES)
        self.assertEqual(actual, expected, 'Failed to match SEMICOLON')

        #fail to match garbage
        target = 'garbage'
        expected = None
        actual = MatchKeyName(target, KEY_NAMES)
        self.assertEqual(actual, expected, 'Found a match to garbage')

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

    def test_NamedColorAndTransparencyInText(self):

        #formatted text
        name = "say"
        text = "Yay!"
        color = "#000000"
        background = "white"
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
        target = SlashCommand(repr="bindloadfile_silent \".\\TestReferences\\Jock Tamson\\MouseChord2.txt\"")
        self.assertEqual(target.IsLoadFileCommand(), True, "Unexpectedly did not set silent IsLoadFileCommand") 
        self.assertEqual(target.GetTargetFile(), os.path.abspath(".\\TestReferences\\Jock Tamson\\MouseChord2.txt"), "Did not get expected TargetFile")
        target.SetTargetFile(".\\NewPath\\Jock Tamson\\MouseChord2.txt")
        self.assertEqual(target.GetTargetFile(), os.path.abspath(".\\NewPath\\Jock Tamson\\MouseChord2.txt"), "Did not set expected TargetFile")

    def test_Clone(self):
        target = SlashCommand(repr="say This test failed")
        actual = target.Clone()
        actual.Name = 'em'
        actual.Text = 'This test passed'
        self.assertNotEqual(actual.Name, target.Name, 'Name not different')
        self.assertNotEqual(actual.Text, target.Text, 'Text not different')
        self.assertEqual(actual.Name, 'em', 'Name not changed')
        self.assertEqual(actual.Text, 'This test passed', 'Text not changed')

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

    def test_GetKeyWithChord(self):

        target = Bind(repr = "PERIOD \"say This test passed\"")
        expected = "PERIOD"
        actual = target.GetKeyWithChord()
        self.assertEqual(actual, expected, 'Did not get expected non-chorded key')
        expected = "."
        actual = target.GetKeyWithChord(defaultNames=True)
        self.assertEqual(actual, expected, 'Did not get expected defaulted non-chorded key')
       
        target = Bind(repr = "shift+PERIOD \"say This test passed\"")
        expected = "shift+PERIOD"
        actual = target.GetKeyWithChord()
        self.assertEqual(actual, expected, 'Did not get expected chorded key')
        expected = "SHIFT+."
        actual = target.GetKeyWithChord(defaultNames=True)
        self.assertEqual(actual, expected, 'Did not get expected defaulted chorded key')
       
        target = Bind(repr = "whoknows+whatthisis \"say This test passed\"")
        expected = "whoknows+whatthisis"
        actual = target.GetKeyWithChord()
        self.assertEqual(actual, expected, 'Did not get expected chorded nonsense')
        actual = target.GetKeyWithChord(defaultNames=True)
        self.assertEqual(actual, expected, 'Did not get expected defaulted chorded nonsense')

    def test_Clone(self):
        target = Bind(repr = "SHIFT+A \"say This test failed $$ emote No!\"")
        actual = target.Clone()
        actual.Key = "B"
        actual.Chord = "ALT"
        actual.Commands[0].Name = "em"
        actual.Commands[0].Text = "This test passed"
        actual.Commands[1].Name = "say"
        actual.Commands[1].Text = "Yay!"
        self.assertNotEqual(actual.Key, target.Key, 'Key not different')
        self.assertNotEqual(actual.Chord, target.Chord, 'Chord not different')
        self.assertNotEqual(actual.Commands[0].Name, target.Commands[0].Name, 'Commands[0].Name not different')
        self.assertNotEqual(actual.Commands[0].Text, target.Commands[0].Text, 'Commands[0].Text not different')
        self.assertNotEqual(actual.Commands[1].Name, target.Commands[1].Name, 'Commands[1].Name not different')
        self.assertNotEqual(actual.Commands[1].Text, target.Commands[1].Text, 'Commands[1].Text not different')
        self.assertEqual(actual.Key, "B", 'Key not changed')
        self.assertEqual(actual.Chord, "ALT", 'Chord not changed')
        self.assertEqual(actual.Commands[0].Name, "em", 'Commands[0].Name not changed')
        self.assertEqual(actual.Commands[0].Text, "This test passed", 'Commands[0].Text not changed')
        self.assertEqual(actual.Commands[1].Name, "say", 'Commands[1].Name not changed')
        self.assertEqual(actual.Commands[1].Text, "Yay!", 'Commands[1].Text not changed')


class TestBindFile(unittest.TestCase):

    def test__repr__(self):
        expected = "A \"say This test passed\"\nB \"emote Yay!\""
        binds = [Bind(key="A", commands=[SlashCommand("say", "This test passed")]), Bind(key="B", commands=[SlashCommand("emote", "Yay!")])]
        target = BindFile(binds)
        actual = str(target)
        self.assertEqual(actual, expected)

    def test_Clone(self):
        input = "A \"say This test failed\"\nB \"emote No!\""
        target = BindFile(filePath="keybinds.txt", repr=input)
        actual = target.Clone()
        actual.FilePath = "new_keybinds.text"
        actual.Binds[0].Key = "C"
        actual.Binds[0].Chord = "SHIFT"
        actual.Binds[0].Commands[0].Name = "em"
        actual.Binds[0].Commands[0].Text = "This test passed"
        actual.Binds[1].Key = "D"
        actual.Binds[1].Chord = "ALT"
        actual.Binds[1].Commands[0].Name = "say"
        actual.Binds[1].Commands[0].Text = "Yes!"
        self.assertNotEqual(actual.FilePath, target.FilePath, "FilePath not different")
        self.assertNotEqual(actual.Binds[0].Key, target.Binds[0].Key, "Binds[0].Key not different")
        self.assertNotEqual(actual.Binds[0].Chord, target.Binds[0].Chord, "Binds[0].Chord not different")
        self.assertNotEqual(actual.Binds[0].Commands[0].Name, target.Binds[0].Commands[0].Name, "Binds[0].Command[0].Name not different")
        self.assertNotEqual(actual.Binds[0].Commands[0].Text, target.Binds[0].Commands[0].Text, "Binds[0].Command[0].Text not different")
        self.assertNotEqual(actual.Binds[1].Key, target.Binds[1].Key, "Binds[0].Key not different")
        self.assertNotEqual(actual.Binds[1].Chord, target.Binds[1].Chord, "Binds[0].Chord not different")
        self.assertNotEqual(actual.Binds[1].Commands[0].Name, target.Binds[1].Commands[0].Name, "Binds[0].Command[0].Name not different")
        self.assertNotEqual(actual.Binds[1].Commands[0].Text, target.Binds[1].Commands[0].Text, "Binds[0].Command[0].Text not different")
        self.assertEqual(actual.FilePath, "new_keybinds.text", "FilePath not different")
        self.assertEqual(actual.Binds[0].Key, "C", "Binds[0].Key not different")
        self.assertEqual(actual.Binds[0].Chord, "SHIFT", "Binds[0].Chord not different")
        self.assertEqual(actual.Binds[0].Commands[0].Name, "em", "Binds[0].Command[0].Name not different")
        self.assertEqual(actual.Binds[0].Commands[0].Text, "This test passed", "Binds[0].Command[0].Text not different")
        self.assertEqual(actual.Binds[1].Key, "D", "Binds[0].Key not different")
        self.assertEqual(actual.Binds[1].Chord, "ALT", "Binds[0].Chord not different")
        self.assertEqual(actual.Binds[1].Commands[0].Name, "say", "Binds[0].Command[0].Name not different")
        self.assertEqual(actual.Binds[1].Commands[0].Text, "Yes!", "Binds[0].Command[0].Text not different")

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
        expected_Alt_Names = "shift+period \"em this test passed\""
        input = "%s\n%s\n%s\n%s\n" % (expected_2, expected_CTRL_2, expected_SHIFT_2, expected_Alt_Names)
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
        actual = target.GetBindForKey(key=".", chord="SHIFT")
        self.assertEqual(1, len(actual))
        self.assertEqual(expected_Alt_Names, str(actual[0]))

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
        actual = GetKeyChains(target, path)
        self.assertEqual(len(actual), 3)
        self.assertEqual(actual[0].Key, "I")
        self.assertEqual(actual[0].Chord, "")
        self.assertEqual(len(actual[0].BoundFiles), 2)
        self.assertEqual(actual[1].Key, "MBUTTON")
        self.assertEqual(actual[1].Chord, "")
        self.assertEqual(len(actual[1].BoundFiles), 2)
        self.assertEqual(actual[2].Key, "NUMPAD0")
        self.assertEqual(actual[2].Chord, "SHIFT")
        self.assertEqual(len(actual[2].BoundFiles), 1)

    def test_NoBoundPaths(self):
        path = ".\\TestReferences\\Soda Juice\\keybinds.txt"
        target = ReadBindsFromFile(path)
        actual = GetKeyChains(target, path)
        self.assertEqual(actual, None)

    def test_Load(self):
        target = BindFileCollection()
        target.Load(".\\TestReferences\\Field Test\\keybinds.txt")
        actual = target.KeyChains
        self.assertEqual(len(actual), 3)
        self.assertEqual(actual[0].Key, "I")
        self.assertEqual(actual[0].Chord, "")
        self.assertEqual(len(actual[0].BoundFiles), 2)
        self.assertEqual(actual[1].Key, "MBUTTON")
        self.assertEqual(actual[1].Chord, "")
        self.assertEqual(len(actual[1].BoundFiles), 2)
        self.assertEqual(actual[2].Key, "NUMPAD0")
        self.assertEqual(actual[2].Chord, "SHIFT")
        self.assertEqual(len(actual[2].BoundFiles), 1)


    def test_NonCircularChain(self):
        target = BindFileCollection()
        target.Load(".\\TestReferences\\Jock Tamson\\keybinds.txt")
        actual = target.KeyChains
        self.assertEqual(len(actual), 2)
        self.assertEqual(actual[0].Key, "MBUTTON")
        self.assertEqual(actual[0].Chord, "")
        self.assertEqual(len(actual[0].BoundFiles), 2)
        self.assertEqual(actual[1].Key, "MOUSECHORD")
        self.assertEqual(actual[1].Chord, "")
        self.assertEqual(len(actual[1].BoundFiles), 4)

    def test_RepointBindFileCollection(self):

        def _compare():
            for idx, entry in enumerate(expected):
                filePath = entry[0]
                boundFilePaths = entry[1]
                if (idx == 0):
                    self.assertEqual(target.FilePath, filePath)
                    bindFile = target.File
                    rootBoundFiles = target.GetBoundFiles()
                else:
                    bindFile = rootBoundFiles[idx - 1]
                self.assertEqual(bindFile.FilePath, filePath)
                actualBoundFilePaths = []
                for bind in bindFile.GetLoadFileBinds():
                    for command in bind.GetLoadFileCommands():
                        actualBoundFilePaths.append(command.GetTargetFile())
                for boundFileIndex, boundFilePath in enumerate(boundFilePaths):
                    self.assertEqual(actualBoundFilePaths[boundFileIndex], boundFilePath, "Did not find expected path for idx " + str(idx))

        target = BindFileCollection()
        target.Load(".\\TestReferences\\Field Test\\keybinds.txt")
        target.RepointFilePaths(".\\NewPath\\Field Test\\keybinds.txt")
        expected = [
            (os.path.abspath(".\\NewPath\\Field Test\\keybinds.txt" ) , [os.path.abspath(p) for p in [
            "./NewPath/Field Test/I1.txt", 
            "./NewPath/Field Test/MBUTTON1.txt", 
            "./NewPath/Field Test/keybinds.txt", 
            "./TestReferences/keybinds(1).txt"]]),
            (os.path.abspath(".\\NewPath\\Field Test\\I1.txt" ) , [os.path.abspath(p) for p in [
            "./NewPath/Field Test/I2.txt"]]),
            (os.path.abspath(".\\NewPath\\Field Test\\I2.txt" ) , [os.path.abspath(p) for p in [
            "./NewPath/Field Test/I1.txt"]]),
            (os.path.abspath(".\\NewPath\\Field Test\\MBUTTON1.txt" ) , [os.path.abspath(p) for p in [
            "./NewPath/Field Test/MBUTTON2.txt"]]),
            (os.path.abspath(".\\NewPath\\Field Test\\MBUTTON2.txt" ) , [os.path.abspath(p) for p in [
            "./NewPath/Field Test/MBUTTON1.txt"]])]
        _compare()
        
        target = BindFileCollection()
        target.Load(".\\TestReferences\\Field Test\\keybinds.txt")
        target.RepointFilePaths(".\\TestReferences\\Field Test\\new_keybinds.txt")
        expected = [
            (os.path.abspath(".\\TestReferences\\Field Test\\new_keybinds.txt" ) , [os.path.abspath(p) for p in [
            "./TestReferences/Field Test/I1(1).txt", 
            "./TestReferences/Field Test/MBUTTON1(1).txt", 
            "./TestReferences/Field Test/new_keybinds.txt", 
            "./TestReferences/keybinds(1).txt"]]),
            (os.path.abspath(".\\TestReferences\\Field Test\\I1(1).txt" ) , [os.path.abspath(p) for p in [
            "./TestReferences/Field Test/I2(1).txt"]]),
            (os.path.abspath(".\\TestReferences\\Field Test\\I2(1).txt" ) , [os.path.abspath(p) for p in [
            "./TestReferences/Field Test/I1(1).txt"]]),
            (os.path.abspath(".\\TestReferences\\Field Test\\MBUTTON1(1).txt" ) , [os.path.abspath(p) for p in [
            "./TestReferences/Field Test/MBUTTON2(1).txt"]]),
            (os.path.abspath(".\\TestReferences\\Field Test\\MBUTTON2(1).txt" ) , [os.path.abspath(p) for p in [
            "./TestReferences/Field Test/MBUTTON1(1).txt"]])]
        _compare()
        
        target = BindFileCollection()
        target.Load(".\\TestReferences\\Field Test\\keybinds.txt")
        target.RepointFilePaths("C:\\keybinds.txt")
        expected = [
            (os.path.abspath("C:\\keybinds.txt" ) , [os.path.abspath(p) for p in [
            "C:\\I1.txt", 
            "C:\\MBUTTON1.txt", 
            "C:\\keybinds.txt", 
            "./TestReferences/keybinds(1).txt"]]),
            (os.path.abspath("C:\\I1.txt" ) , [os.path.abspath(p) for p in [
            "C:\\I2.txt"]]),
            (os.path.abspath("C:\\I2.txt" ) , [os.path.abspath(p) for p in [
            "C:\\I1.txt"]]),
            (os.path.abspath("C:\\MBUTTON1.txt" ) , [os.path.abspath(p) for p in [
            "C:\\MBUTTON2.txt"]]),
            (os.path.abspath("C:\\MBUTTON2.txt" ) , [os.path.abspath(p) for p in [
            "C:\\MBUTTON1.txt"]])]
        _compare()

    def test_New(self):
        target = BindFileCollection()
        target.New()
        self.assertEqual(None, target.File.Binds, "Unexpected empty bind length")
        target.New(defaults=True)
        self.assertEqual(99, len(target.File.Binds), "Unexpected default bind length")
        self.assertEqual("'", target.File.Binds[0].Key, "Unexpected default key")
        self.assertEqual("quickchat", target.File.Binds[0].Commands[0].Name, "Unexpected default command")
        self.assertEqual("", target.File.Binds[0].Commands[0].Text, "Unexpected default command text")

    def test_Serialization(self):
        filePath = "temp.json"
        collectionFilePath = os.path.abspath(".\\TestReferences\\Jock Tamson\\keybinds.txt")
        if (path.exists(filePath)):
            remove(filePath)
        try:
            target = BindFileCollection()
            target.Load(collectionFilePath)
            target.Serialize(filePath)
            target = BindFileCollection()
            target.Deserialize(filePath)
            expected = BindFileCollection()
            expected.Load(collectionFilePath)
            expected.RepointFilePaths("C:\\keybinds.txt", True)
            self.assertEqual(target.File.FilePath, expected.File.FilePath, "Unexpedted name following round trip")
            self.assertEqual(target.File.__repr__(), expected.File.__repr__(), "Unexpected repr following round trip")
            binds = target.GetBoundFiles()
            expectedBinds = expected.GetBoundFiles()
            self.assertEqual(len(binds), len(expectedBinds), "Did not find expected number of bound files") 
            for idx, expectedBind in enumerate(expectedBinds):
                self.assertEqual(binds[idx].FilePath, expectedBind.FilePath, "Did not find expected path for bound file " + str(idx))
                self.assertEqual(binds[idx].__repr__(), expectedBind.__repr__(), "Did not find expected repr for bound file " + str(idx))
        finally:
            if (path.exists(filePath)):
                remove(filePath)
     
class TestKeychain(unittest.TestCase):

    def test_Keychain(self):
        key = "MOUSECHORD"
        chord = "SHIFT"
        file1 = BindFile(repr="SHIFT+MOUSECHORD bind_load_file \"MOUSECHORD2.txt\"", filePath="MOUSECHORD1.txt")
        file2 = BindFile(repr="SHIFT+MOUSECHORD bind_load_file \"MOUSECHORD1.txt\"", filePath="MOUSECHORD2.txt")
        target = Keychain(key=key, chord=chord, boundFiles=[file1, file2])
        actual = target.__repr__()
        expected = '{\'key\': \'MOUSECHORD\', \'chord\': \'SHIFT\', \'bound_files\': [{\'path\': \'MOUSECHORD1.txt\', \'repr\': \'SHIFT+MOUSECHORD "bind_load_file "MOUSECHORD2.txt""\'}, {\'path\': \'MOUSECHORD2.txt\', \'repr\': \'SHIFT+MOUSECHORD "bind_load_file "MOUSECHORD1.txt""\'}]}'
        self.assertEqual(actual, expected)
        expected2 = expected.replace('MOUSECHORD', 'NUMPAD0', 1)
        expected2 = expected.replace('SHIFT', '', 1)
        target = Keychain(repr=expected2)
        actual = target.__repr__()
        self.assertEqual(actual, expected2)
        clone = target.Clone()
        clone.Key = 'MOUSECHORD'
        clone.Chord = 'SHIFT'
        actual = clone.__repr__()
        self.assertEqual(actual, expected)
        actual = target.__repr__()
        self.assertEqual(actual, expected2)




if __name__ == "__main__":
    unittest.main()

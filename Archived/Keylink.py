import os

from Keystone.Model.Bind import Bind
from Keystone.Model.BindFile import BindFile
from Keystone.Utility.KeystoneUtils import GetFileName, RemoveOuterQuotes


class Keylink():

    def __init__(self, bindFile: BindFile, key: str, chord: str = ""):
        self.File = bindFile
        self.FilePath = os.path.abspath(bindFile.FilePath)
        self.Key = key
        self.Chord = chord
        self.Bind = None
        for bind in [b for b in bindFile.Binds if ((b.Key == key) and (b.Chord == chord))]:
            self.Bind = bind
        self.Command = None
        for command in [c for c in self.Bind.Commands if c.IsLoadFileCommand()]:
            self.Command = command
        targetFilePath = (RemoveOuterQuotes(self.Command.Text))
        if targetFilePath == "":
            self.TargetFilePath = ""
        else:
            self.TargetFilePath = os.path.abspath(targetFilePath)

    def ChangeKey(self, key):
        self.Key = key
        self.Bind.Key = key

    def ChangeChord(self, chord):
        self.Chord = chord
        self.Bind.Chord = chord

    def ChangeFilePath(self, filePath):
        self.FilePath = filePath
        self.File.FilePath = filePath

    def ChangeTargetFilePath(self, targetFilePath):
        self.TargetFilePath = os.path.abspath(targetFilePath)
        self.Command.Text = "\"" + self.TargetFilePath + "\""


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
   
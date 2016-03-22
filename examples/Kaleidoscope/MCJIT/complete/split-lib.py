#!/usr/bin/env python

class TimingScriptGenerator:
    """Used to generate a bash script which will invoke the toy and time it"""
    def __init__(self, scriptname, outputname):
        self.shfile = open(scriptname, 'w')
        self.timeFile = outputname
        self.shfile.write("echo \"\" > {0!s}\n".format(self.timeFile))

    def writeTimingCall(self, irname, callname):
        """Echo some comments and invoke both versions of toy"""
        rootname = irname
        if '.' in irname:
            rootname = irname[:irname.rfind('.')]
        self.shfile.write("echo \"{0!s}: Calls {1!s}\" >> {2!s}\n".format(callname, irname, self.timeFile))
        self.shfile.write("echo \"\" >> {0!s}\n".format(self.timeFile))
        self.shfile.write("echo \"With MCJIT\" >> {0!s}\n".format(self.timeFile))
        self.shfile.write("/usr/bin/time -f \"Command %C\\n\\tuser time: %U s\\n\\tsytem time: %S s\\n\\tmax set: %M kb\"")
        self.shfile.write(" -o {0!s} -a ".format(self.timeFile))
        self.shfile.write("./toy -suppress-prompts -use-mcjit=true -enable-lazy-compilation=true -use-object-cache -input-IR={0!s} < {1!s} > {2!s}-mcjit.out 2> {3!s}-mcjit.err\n".format(irname, callname, rootname, rootname))
        self.shfile.write("echo \"\" >> {0!s}\n".format(self.timeFile))
        self.shfile.write("echo \"With MCJIT again\" >> {0!s}\n".format(self.timeFile))
        self.shfile.write("/usr/bin/time -f \"Command %C\\n\\tuser time: %U s\\n\\tsytem time: %S s\\n\\tmax set: %M kb\"")
        self.shfile.write(" -o {0!s} -a ".format(self.timeFile))
        self.shfile.write("./toy -suppress-prompts -use-mcjit=true -enable-lazy-compilation=true -use-object-cache -input-IR={0!s} < {1!s} > {2!s}-mcjit.out 2> {3!s}-mcjit.err\n".format(irname, callname, rootname, rootname))
        self.shfile.write("echo \"\" >> {0!s}\n".format(self.timeFile))
        self.shfile.write("echo \"With JIT\" >> {0!s}\n".format(self.timeFile))
        self.shfile.write("/usr/bin/time -f \"Command %C\\n\\tuser time: %U s\\n\\tsytem time: %S s\\n\\tmax set: %M kb\"")
        self.shfile.write(" -o {0!s} -a ".format(self.timeFile))
        self.shfile.write("./toy -suppress-prompts -use-mcjit=false -input-IR={0!s} < {1!s} > {2!s}-mcjit.out 2> {3!s}-mcjit.err\n".format(irname, callname, rootname, rootname))
        self.shfile.write("echo \"\" >> {0!s}\n".format(self.timeFile))
        self.shfile.write("echo \"\" >> {0!s}\n".format(self.timeFile))

class LibScriptGenerator:
    """Used to generate a bash script which will invoke the toy and time it"""
    def __init__(self, filename):
        self.shfile = open(filename, 'w')

    def writeLibGenCall(self, libname, irname):
        self.shfile.write("./toy -suppress-prompts -use-mcjit=false -dump-modules < {0!s} 2> {1!s}\n".format(libname, irname))

def splitScript(inputname, libGenScript, timingScript):
  rootname = inputname[:-2]
  libname = rootname + "-lib.k"
  irname = rootname + "-lib.ir"
  callname = rootname + "-call.k"
  infile = open(inputname, "r")
  libfile = open(libname, "w")
  callfile = open(callname, "w")
  print "Splitting {0!s} into {1!s} and {2!s}".format(inputname, callname, libname)
  for line in infile:
    if not line.startswith("#"):
      if line.startswith("print"):
        callfile.write(line)
      else:
        libfile.write(line)
  libGenScript.writeLibGenCall(libname, irname)
  timingScript.writeTimingCall(irname, callname)

# Execution begins here
libGenScript = LibScriptGenerator("make-libs.sh")
timingScript = TimingScriptGenerator("time-lib.sh", "lib-timing.txt")

script_list = ["test-5000-3-50-50.k", "test-5000-10-100-10.k", "test-5000-10-5-10.k", "test-5000-10-1-0.k", 
               "test-1000-3-10-50.k", "test-1000-10-100-10.k", "test-1000-10-5-10.k", "test-1000-10-1-0.k",
               "test-200-3-2-50.k", "test-200-10-40-10.k", "test-200-10-2-10.k", "test-200-10-1-0.k"]

for script in script_list:
  splitScript(script, libGenScript, timingScript)
print "All done!"
